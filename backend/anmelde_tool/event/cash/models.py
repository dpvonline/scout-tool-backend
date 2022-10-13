import uuid

from django.contrib.auth import get_user_model
from django.db import models
from anmelde_tool.event import models as event_models

User = get_user_model()


class CashIncome(models.Model):
    id = models.UUIDField(auto_created=True, primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.FloatField(default=0)
    transfer_subject = models.CharField(max_length=250, blank=True)
    transfer_date = models.DateTimeField(null=True, blank=True)
    transfer_person = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    transfer_reference_id = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=250, blank=True, null=True)
    registration = models.ForeignKey(event_models.Registration, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.registration}: {self.amount}'
