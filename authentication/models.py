import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from anmelde_tool.event.choices import choices as event_choices
from authentication.choices import BundesPostTextChoice, RequestGroupAccessChoices
from authentication.choices import EmailNotificationType
from backend.timestamp_mixin import TimeStampMixin
from basic import models as basic_models
from basic.choices import Gender
from keycloak_auth.models import KeycloakGroup


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, blank=False)
    scout_organisation = models.ForeignKey(basic_models.ScoutHierarchy, on_delete=models.PROTECT, null=True, blank=True)
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    scout_name = models.CharField(max_length=20, blank=True, null=True)
    dsgvo_confirmed = models.BooleanField(default=False, null=True)
    email_notification = models.CharField(
        max_length=10,
        choices=EmailNotificationType.choices,
        default=EmailNotificationType.FULL,
    )
    password = models.CharField(max_length=128, blank=True, null=True)
    sms_notification = models.BooleanField(default=True)
    keycloak_id = models.CharField(max_length=32, blank=True, null=True)

    def __str__(self):
        return self.username


class Person(TimeStampMixin):
    """
    Model to save a natural person with or without login
    """
    id = models.UUIDField(auto_created=True, primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True)
    scout_name = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=100, default="")
    last_name = models.CharField(max_length=100, default="")
    address = models.CharField(max_length=200, blank=True, null=True)
    address_supplement = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.ForeignKey(basic_models.ZipCode, on_delete=models.PROTECT, null=True, blank=True)
    scout_group = models.ForeignKey(basic_models.ScoutHierarchy, on_delete=models.PROTECT, null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    phone_number_verified = models.BooleanField(default=0)
    email = models.EmailField(null=True, blank=True)
    email_verified = models.BooleanField(default=0)
    bundespost = models.CharField(
        max_length=13,
        choices=BundesPostTextChoice.choices,
        default=BundesPostTextChoice.NOTHING
    )
    birthday = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=1,
        choices=Gender.choices,
        default=Gender.Nothing
    )
    active = models.BooleanField(default=False)
    person_verified = models.BooleanField(default=False)
    eat_habits = models.ManyToManyField(basic_models.EatHabit, blank=True)
    leader = models.CharField(
        max_length=6,
        choices=event_choices.LeaderTypes.choices,
        default=event_choices.LeaderTypes.KeineFuehrung
    )
    scout_level = models.CharField(
        max_length=6,
        choices=event_choices.ScoutLevelTypes.choices,
        default=event_choices.ScoutLevelTypes.Unbekannt
    )
    created_by = models.ManyToManyField(CustomUser, related_name='creator')


class RequestGroupAccess(TimeStampMixin):
    id = models.UUIDField(auto_created=True, primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, related_name='user')
    group = models.ForeignKey(KeycloakGroup, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(
        max_length=8,
        choices=RequestGroupAccessChoices.choices,
        default=RequestGroupAccessChoices.NONE
    )
    checked_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='checked_by')
