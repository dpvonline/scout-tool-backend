import uuid

from django.contrib.auth import get_user_model
from django.db import models

from anmelde_tool.event.choices import choices as event_choices
from anmelde_tool.registration.models import Registration, RegistrationParticipant
from authentication.models import CustomUser
from basic import models as basic_models

User: CustomUser = get_user_model()


class Workshop(basic_models.TimeStampMixin):
    id = models.UUIDField(auto_created=True, primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    free_text = models.CharField(max_length=10000, blank=True)
    price = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    price_per_person = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    min_person = models.IntegerField(blank=True, null=True)
    max_person = models.IntegerField(blank=True, null=True)
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)
    type = models.CharField(
        max_length=1,
        choices=event_choices.WorkshopType.choices,
        default=event_choices.WorkshopType.Workshop
    )
    duration = models.IntegerField(default=60)
    can_be_repeated = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class WorkshopParticipant(basic_models.TimeStampMixin):
    id = models.AutoField(primary_key=True)
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, null=True)
    participant = models.ForeignKey(RegistrationParticipant, on_delete=models.CASCADE, null=True)
