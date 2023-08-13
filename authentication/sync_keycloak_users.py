from celery import shared_task
from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model

from authentication.models import CustomUser
from backend.OIDCAuthentication import MyOIDCAB
from backend.settings import keycloak_admin

User: CustomUser = get_user_model()

logger = get_task_logger(__name__)


@shared_task
def import_keycloak_members():
    logger.info('Starting syncing Keycloak users')
    oicd = MyOIDCAB()

    query = {
        'max': -1,
        'enabled': True,
        'briefRepresentation': True,
        'emailVerified': True,
    }
    all_keycloak_users = keycloak_admin.get_users(query)
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

            if isinstance(verband, list):
                verband = verband[0]

            if isinstance(bund, list):
                bund = bund[0]

            if isinstance(fahrtenname, list):
                fahrtenname = fahrtenname[0]

            if isinstance(stamm, list):
                stamm = stamm[0]
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
        count += 1

    logger.info(f'{count} Users have been added')
