from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model

from authentication.models import CustomUser, Person
from backend.OIDCAuthentication import MyOIDCAB
from backend.settings import keycloak_admin

User: CustomUser = get_user_model()

logger = get_task_logger(__name__)


@shared_task
def import_keycloak_members():
    logger.info('Starting syncing Keycloak users')
    oicd = MyOIDCAB()

    queury = {
        'max': -1,
        'enabled': True,
        'briefRepresentation': True,
        'emailVerified': True,
    }
    all_keycloak_users = keycloak_admin.get_users(queury)
    all_keycloak_users_ids = [val['id'] for val in all_keycloak_users]
    all_django_users_ids = list(User.objects.all().values_list('keycloak_id', flat=True))
    missing_ids = list(set(all_keycloak_users_ids) - set(all_django_users_ids))

    count = 0
    for keycloak_id in missing_ids:
        if not keycloak_id:
            continue
        keycloak_user = keycloak_admin.get_user(keycloak_id)

        if not keycloak_user.get('email'):
            continue

        verband = ''
        bund = ''
        fahrtenname = ''
        stamm = ''

        attributes = keycloak_user.get('attributes')
        if attributes:
            verband = attributes.get('verband', '')
            bund = attributes.get('bund', '')
            fahrtenname = attributes.get('fahrtenname', '')
            stamm = attributes.get('stamm', '')

        claim = {
            'sub': keycloak_user.get('id', ''),
            'email_verified': keycloak_user.get('firstName', ''),
            'verband': verband,
            'fahrtenname': fahrtenname,
            'bund': bund,
            'stamm': stamm,
            'nickname': fahrtenname,
            'preferred_username': keycloak_user.get('username', ''),
            'given_name': keycloak_user.get('firstName', ''),
            'family_name': keycloak_user.get('lastName', ''),
            'email': keycloak_user.get('email', ''),
        }
        django_user = oicd.create_user(claim)
        django_user.person = Person.objects.create()
        django_user.save()
        count += 1

    logger.info(f'{count} Users have been added')
