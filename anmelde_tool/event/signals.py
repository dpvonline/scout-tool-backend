from anmelde_tool.email_services import services
from anmelde_tool.registration.models import Registration


#
# def pre_delete_registration(sender, instance: event_models.Registration, **kwargs):
#     for tag in instance.tags.all():
#         tag.delete()


def post_save_registration(sender: Registration, instance: Registration, update_fields, raw, **kwargs):
    if update_fields and 'is_confirmed' in update_fields and instance.is_confirmed:
        services.send_registration_created_mail(instance_id=str(instance.id))
