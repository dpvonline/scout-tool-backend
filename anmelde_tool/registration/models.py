import uuid

from django.contrib.auth import get_user_model
from django.db import models

from anmelde_tool.event.choices import choices as event_choices
from anmelde_tool.event.models import Event, BookingOption
from authentication.models import CustomUser
from basic import choices as basic_choices
from basic import models as basic_models
from authentication import models as auth_models

User: CustomUser = get_user_model()


# Create your models here.
class Registration(basic_models.TimeStampMixin):
    """
    is_confirmed = the registrator confirms that the current state of the registration is complete in the last step of
        the registration
    """
    id = models.UUIDField(auto_created=True, primary_key=True, default=uuid.uuid4, editable=False)
    scout_organisation = models.ForeignKey(basic_models.ScoutHierarchy, null=True, on_delete=models.PROTECT)
    responsible_persons = models.ManyToManyField(User)
    is_confirmed = models.BooleanField(default=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.event.name}: {self.scout_organisation.name}"


class RegistrationParticipant(basic_models.TimeStampMixin):
    scout_name = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=100, default="Generated")
    last_name = models.CharField(max_length=100, default="Generated")
    address = models.CharField(max_length=100, blank=True)
    zip_code = models.ForeignKey(basic_models.ZipCode, on_delete=models.PROTECT, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    scout_group = models.ForeignKey(basic_models.ScoutHierarchy, on_delete=models.PROTECT, null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(null=True, blank=True)
    birthday = models.DateTimeField(null=True, blank=True)
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE, null=True, blank=True)
    booking_option = models.ForeignKey(BookingOption, on_delete=models.SET_NULL, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=basic_choices.Gender.choices, default=basic_choices.Gender.Nothing)
    generated = models.BooleanField(default=False)
    eat_habit = models.ManyToManyField(basic_models.EatHabit, blank=True)
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
    person = models.ForeignKey(auth_models.Person, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return f"{self.registration}: {self.last_name}, {self.first_name}"
