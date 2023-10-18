import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import models

from anmelde_tool.email_services import models as email_services_model
from authentication.models import CustomUser
from basic import models as basic_models
from keycloak_auth import models as keycloak_models

User: CustomUser = get_user_model()


class EventLocation(basic_models.TimeStampMixin):
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=200, blank=True)
    zip_code = models.ForeignKey(basic_models.ZipCode, on_delete=models.PROTECT, null=True, blank=True)
    address = models.CharField(max_length=60, blank=True)
    contact_name = models.CharField(max_length=30, blank=True)
    contact_email = models.CharField(max_length=30, blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    per_person_fee = models.FloatField(blank=True, null=True)
    fix_fee = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f'{self.name}: ({self.address}, {self.zip_code})'


class Event(basic_models.TimeStampMixin):
    id = models.UUIDField(auto_created=True, primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    technical_name = models.CharField(max_length=15, null=True, blank=True)
    short_description = models.CharField(max_length=100, blank=True)
    long_description = models.CharField(max_length=10000, blank=True)
    cloud_link = models.CharField(max_length=200, blank=True, null=True)
    event_url = models.CharField(max_length=200, blank=True, null=True)
    icon = models.CharField(max_length=20, blank=True, null=True)
    location = models.ForeignKey(EventLocation, on_delete=models.PROTECT, null=True, blank=True)
    start_date = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    end_date = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    registration_deadline = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    registration_start = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    last_possible_update = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    is_public = models.BooleanField(default=False)
    responsible_persons = models.ManyToManyField(User)
    view_group = models.ForeignKey(
        keycloak_models.KeycloakGroup,
        on_delete=models.SET_NULL,
        related_name='view_group',
        blank=True,
        null=True
    )
    admin_group = models.ForeignKey(
        keycloak_models.KeycloakGroup,
        on_delete=models.SET_NULL,
        related_name='admin_group',
        blank=True,
        null=True
    )
    view_allow_subgroup = models.BooleanField(default=False)
    inviting_group = models.ForeignKey(
        keycloak_models.KeycloakGroup,
        on_delete=models.SET_NULL,
        related_name='inviting_group',
        null=True,
        blank=True
    )
    invited_groups = models.ManyToManyField(
        keycloak_models.KeycloakGroup,
        related_name='invited_groups',
        blank=True
    )
    registration_level = models.ForeignKey(
        basic_models.ScoutOrgaLevel,
        on_delete=models.SET_DEFAULT,
        default=5
    )
    theme = models.ForeignKey(
        basic_models.FrontendTheme,
        on_delete=models.SET_NULL,
        default=1,
        null=True,
        blank=True
    )
    email_set = models.ForeignKey(
        email_services_model.StandardEmailRegistrationSet,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    def __str__(self):
        return f"{self.name}"


class EventModule(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=100, default='', blank=True)
    header = models.CharField(max_length=100, default='Default Header')
    description = models.TextField(default='')
    internal = models.BooleanField(default=False)
    ordering = models.IntegerField(default=999, auto_created=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)
    required = models.BooleanField(default=False)
    standard = models.BooleanField(default=False)

    def __str__(self):
        if self.event:
            return f'{self.name} ({self.event.name})'
        else:
            return f'{self.name}'

class BookingOption(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    tags = models.ManyToManyField(basic_models.Tag, blank=True)
    bookable_from = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    bookable_till = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    event = models.ForeignKey(Event, null=True, on_delete=models.CASCADE)
    max_participants = models.IntegerField(default=0)
    start_date = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    end_date = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)

    def __str__(self):
        return self.name


class StandardEventTemplate(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    introduction = models.ForeignKey(
        EventModule,
        null=True, on_delete=models.PROTECT,
        related_name='introduction'
    )
    summary = models.ForeignKey(
        EventModule,
        null=True,
        on_delete=models.PROTECT,
        related_name='confirmation'
    )
    participants = models.ForeignKey(
        EventModule,
        null=True,
        on_delete=models.PROTECT,
        related_name='participants'
    )
    letter = models.ForeignKey(
        EventModule,
        null=True,
        on_delete=models.PROTECT,
        related_name='letter'
    )
    other_required_modules = models.ManyToManyField(
        EventModule,
        blank=True,
        related_name='other_required_modules'
    )
