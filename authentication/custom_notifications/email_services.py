from celery import shared_task
from django.contrib.auth import get_user_model

from authentication.models import CustomUser
from backend import settings

url = getattr(settings, 'FRONT_URL', '')
email_active = getattr(settings, 'SEND_MAIL', False)

User: CustomUser = get_user_model()


@shared_task
def instant_notification(recipient_id: str):
    recipients = User.objects.get(id=recipient_id)
    print(f'instant notification for: {recipients}')


@shared_task
def hourly_notification(email_type):
    print('hourly notification')
