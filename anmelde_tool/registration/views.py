import re
from datetime import timezone

from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import mixins, viewsets, status
from rest_framework.response import Response

from anmelde_tool.attributes import models as attributes_model
from anmelde_tool.attributes import serializers as attributes_serializer
from anmelde_tool.event import api_exceptions as event_api_exceptions
from anmelde_tool.event import models as event_models
from anmelde_tool.event import permissions as event_permissions
from anmelde_tool.event.choices import choices as event_choices
from anmelde_tool.event.helper import get_registration, custom_get_or_404
from anmelde_tool.registration import serializers as registration_serializers
from anmelde_tool.registration.models import Registration, RegistrationParticipant
from anmelde_tool.registration.serializers import RegistrationParticipantGroupSerializer
from authentication import models as auth_models
from basic import models as basic_models
from basic.models import ZipCode

User = get_user_model()


def create_missing_eat_habits(request) -> [str]:
    eat_habits = request.data.get('eat_habit', [])
    result = []
    for habit in eat_habits:
        if len(habit) > 100:
            raise event_api_exceptions.EatHabitTooLong
        splitted = re.split(',|;', habit)
        for split in splitted:
            split = split.strip().title()
            result.append(split)
            if not basic_models.EatHabit.objects.filter(name__exact=split).exists():
                basic_models.EatHabit.objects.create(name=split)
    return result


# def add_event_attribute(attribute: attributes_model.AbstractAttribute) -> attributes_model.AbstractAttribute:
#     new_attribute: attributes_model.AbstractAttribute = deepcopy(attribute)
#     new_attribute.pk = None
#     new_attribute.id = None
#     new_attribute.template = False
#     new_attribute.template_id = attribute.id
#     new_attribute.save()
#     return new_attribute


class RegistrationSingleParticipantViewSet(viewsets.ModelViewSet):
    permission_classes = [event_permissions.IsSubRegistrationResponsiblePerson]

    def get_queryset(self) -> QuerySet:
        registration_id = self.kwargs.get("registration_pk", None)
        return RegistrationParticipant.objects.filter(
            registration=registration_id
        ).order_by('age')

    def create(self, request, *args, **kwargs) -> Response:
        eat_habits_formatted = create_missing_eat_habits(request)

        if eat_habits_formatted and len(eat_habits_formatted) > 0:
            request.data['eat_habit'] = eat_habits_formatted

        if request.data.get('zip_code'):
            zip_code = get_object_or_404(ZipCode, zip_code=request.data.get('zip_code'))
            request.data['zip_code'] = zip_code.id

        registration: Registration = self.participant_initialization(request)

        if request.data.get('age'):
            request.data['birthday'] = timezone.now() - relativedelta(years=int(request.data.get('age')))
        request.data['registration'] = registration.id

        if request.data.get('first_name') is None and request.data.get('last_name') is None:
            max_num = self.get_queryset().count()
            request.data['first_name'] = 'Teilnehmer'
            request.data['last_name'] = max_num + 1

        if request.data.get('booking_option') is None:
            request.data['booking_option'] = registration.event.bookingoption_set.first().id

        if registration.event.registration_deadline < timezone.now():
            request.data['needs_confirmation'] = event_choices.ParticipantActionConfirmation.AddCompletyNew

        if request.data.get('allow_permanently'):
            person = auth_models.Person(
                first_name=request.data.get('first_name'),
                scout_name=request.data.get('scout_name'),
                last_name=request.data.get('last_name'),
                address=request.data.get('address'),
                address_supplement=request.data.get('address_supplement'),
                scout_group=request.data.get('scout_group'),
                phone_number=request.data.get('phone_number'),
                email=request.data.get('email'),
                zip_code=zip_code,
                gender=request.data.get('gender'),
                scout_level='N'
            )
            person.save()

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs) -> Response:

        eat_habits_formatted = create_missing_eat_habits(request)

        if eat_habits_formatted and len(eat_habits_formatted) > 0:
            request.data['eat_habit'] = eat_habits_formatted

        request.data['generated'] = False
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs) -> Response:
        registration: Registration = self.participant_initialization(request)

        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        serializer = {
            'create': registration_serializers.RegistrationParticipantSerializer,
            'retrieve': registration_serializers.RegistrationParticipantSerializer,
            'list': registration_serializers.RegistrationParticipantShortSerializer,
            'update': registration_serializers.RegistrationParticipantSerializer,
            'destroy': registration_serializers.RegistrationParticipantSerializer
        }
        return serializer.get(self.action, registration_serializers.RegistrationParticipantPutSerializer)

    def participant_initialization(self, request) -> Registration:
        input_serializer = registration_serializers.RegistrationParticipantPutSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        registration_id = self.kwargs.get("registration_pk", None)
        registration: Registration = get_registration(registration_id)

        if not event_permissions.IsEventSuperResponsiblePerson:
            if registration.event.registration_start > timezone.now():
                raise event_api_exceptions.TooEarly
            elif self.action != 'destroy' and registration.event.last_possible_update < timezone.now():
                raise event_api_exceptions.TooLate

        return registration


class RegistrationAddGroupParticipantViewSet(viewsets.ViewSet):
    permission_classes = [event_permissions.IsSubRegistrationResponsiblePerson]
    serializer_class = registration_serializers.RegistrationParticipantShortSerializer

    def create(self, request, *args, **kwargs) -> Response:
        registration: Registration = self.participant_group_initialization(request)
        number: int = request.data.get('number', 0)
        scout_level: int = request.data.get('scout_level', 'N')
        eat_habit_id: int = request.data.get('eat_habit', 1)
        existing_participants: QuerySet = RegistrationParticipant.objects.filter(
            registration=registration.id
        )
        total_participant_count: int = existing_participants.count()

        new_participants = []

        confirm = ParticipantActionConfirmation.Nothing

        switcher = {
            'N': 14,
            'W': 9,
            'S': 14,
            'R': 18,
        }
        print(scout_level)
        if scout_level:
            age = switcher.get(scout_level, 14)
            print(age)
            birthday = timezone.now() - relativedelta(years=int(age))
            print(birthday)

        booking: event_models.BookingOption = registration.event.bookingoption_set.first()
        if eat_habit_id:
            eat_habit: basic_models.EatHabit = get_object_or_404(basic_models.EatHabit, id=eat_habit_id)
        for i in range(total_participant_count + 1, total_participant_count + int(number) + 1):
            participant = RegistrationParticipant(
                first_name='Teilnehmender',
                scout_name=f'Teilnehmender',
                last_name=i,
                age=age,
                birthday=birthday,
                scout_level=scout_level,
                registration=registration,
                generated=True,
                needs_confirmation=confirm,
                booking_option=booking
            )
            participant.save()
            if eat_habit_id:
                participant.eat_habit.add(eat_habit)
            new_participants.append(participant)

        return Response({'created  persons'}, status=status.HTTP_201_CREATED)

    def participant_group_initialization(self, request) -> Registration:
        input_serializer = RegistrationParticipantGroupSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        registration_id = self.kwargs.get("registration_pk", None)
        registration: Registration = get_object_or_404(Registration, id=registration_id)

        if registration.event.registration_start > timezone.now():
            raise event_api_exceptions.TooEarly
        elif self.action != 'destroy' and registration.event.last_possible_update < timezone.now():
            raise event_api_exceptions.TooLate

        return registration


class RegistrationGroupParticipantViewSet(viewsets.ViewSet):
    permission_classes = [event_permissions.IsSubRegistrationResponsiblePerson]
    serializer_class = registration_serializers.RegistrationParticipantShortSerializer

    def create(self, request, *args, **kwargs) -> Response:
        registration: Registration = self.participant_group_initialization(request)
        number: int = request.data.get('number', 0)
        existing_participants: QuerySet = RegistrationParticipant.objects.filter(
            registration=registration.id
        )
        active_participants: QuerySet = existing_participants.filter(deactivated=False)
        inactive_participants: QuerySet = existing_participants.filter(deactivated=True)
        active_participant_count: int = active_participants.count()
        inactive_participant_count: int = inactive_participants.count()
        total_participant_count: int = active_participant_count + inactive_participant_count
        activate = min(inactive_participant_count, number)
        create: int = max(number - total_participant_count, 0)
        confirm_needed: bool = registration.event.registration_deadline < timezone.now()

        if activate > 0:

            RegistrationParticipant.objects \
                .filter(pk__in=inactive_participants.order_by('created_at').values_list('pk', flat=True)[:activate]) \
                .update(deactivated=False)

        if create > 0:
            new_participants = []

            booking: event_models.BookingOption = registration.event.bookingoption_set.first().id

            for i in range(total_participant_count + 1, number + 1):
                participant = RegistrationParticipant(
                    first_name='Pfadi',
                    last_name=i,
                    registration=registration,
                    generated=True,
                    booking_option=booking
                )
                new_participants.append(participant)
            RegistrationParticipant.objects.bulk_create(new_participants)

        return Response({'activated': activate, 'created': create}, status=status.HTTP_201_CREATED)

    def participant_group_initialization(self, request) -> Registration:
        input_serializer = registration_serializers.RegistrationParticipantGroupSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        registration_id = self.kwargs.get("registration_pk", None)
        registration: Registration = get_object_or_404(Registration, id=registration_id)

        if registration.event.registration_start > timezone.now():
            raise event_api_exceptions.TooEarly
        elif self.action != 'destroy' and registration.event.last_possible_update < timezone.now():
            raise event_api_exceptions.TooLate

        return registration

    def delete(self, request, *args, **kwargs) -> Response:
        registration: Registration = self.participant_group_initialization(request)
        number: int = request.data.get('number', 9999)
        all_participants: QuerySet = RegistrationParticipant.objects.filter(registration=registration.id)
        participant_count = all_participants.count()

        if number <= participant_count:
            num_delete: int = max(participant_count - number, 0)
            deletable_participants: QuerySet = all_participants.filter(generated=True)
            deletable_participants_count: int = deletable_participants.count()

            if num_delete < deletable_participants_count:
                selected_deletable_participants = RegistrationParticipant.objects.filter(
                    pk__in=deletable_participants.order_by('-created_at').values_list('pk', flat=True)[:num_delete]
                )
            else:
                selected_deletable_participants = deletable_participants

            selected_deletable_participants.delete()
            return Response({'deleted': num_delete}, status=status.HTTP_204_NO_CONTENT)

        else:
            return Response(
                f'number: {number} is higher or equal than current participantc count {participant_count}',
                status=status.HTTP_400_BAD_REQUEST
            )


class RegistrationAttributeViewSet(viewsets.ModelViewSet):
    permission_classes = [event_permissions.IsSubRegistrationResponsiblePerson]

    def create(self, request, *args, **kwargs) -> Response:
        serializer: attributes_serializer.AbstractAttributePutPolymorphicSerializer = self.get_serializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        registration_id = self.kwargs.get("registration_pk", None)
        registration: Registration = get_object_or_404(Registration, id=registration_id)

        template_attribute: attributes_model.AbstractAttribute = \
            get_object_or_404(attributes_model.AbstractAttribute, pk=serializer.data.get('template_id', -1))

        new_attribute = add_event_attribute(template_attribute)

        serializer.update(new_attribute, serializer.validated_data)

        registration.tags.add(new_attribute.id)

        json = attributes_serializer.AbstractAttributeGetPolymorphicSerializer(new_attribute)
        return Response(json.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs) -> Response:
        super().update(request, *args, **kwargs)
        json = attributes_serializer.AbstractAttributeGetPolymorphicSerializer(self.get_object())
        return Response(json.data, status=status.HTTP_200_OK)

    # def get_serializer_class(self):
    # if self.request.method == 'POST':
    #     return attributes_serializer.AbstractAttributePostPolymorphicSerializer
    # elif self.request.method == 'GET':
    #     return attributes_serializer.AbstractAttributeGetPolymorphicSerializer
    # elif self.request.method == 'PUT':
    #     return attributes_serializer.AbstractAttributePutPolymorphicSerializer
    # else:
    #     return attributes_serializer.AbstractAttributePutPolymorphicSerializer

    def get_queryset(self) -> QuerySet:
        registration_id = self.kwargs.get("registration_pk", None)
        registration: Registration = get_object_or_404(Registration, id=registration_id)
        return registration.tags


class AddResponsiblePersonRegistrationViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    permission_classes = [event_permissions.IsRegistrationResponsiblePerson]
    queryset = Registration.objects.all()
    serializer_class = registration_serializers.RegistrationPutSerializer

    def update(self, request, *args, **kwargs):
        new_responsible_person = request.data.get('responsible_person')

        # get user-id
        new_responsible_person_id = User.objects.filter(email=new_responsible_person).first().id

        instance = self.get_object()

        # prepare the return list with new user
        responsible_person_ids = [new_responsible_person_id]

        # add all existing users-id to list
        for x in instance.responsible_persons.all():
            responsible_person_ids.append(x.id)

        request.data['responsible_persons'] = responsible_person_ids

        return super().update(request, *args, **kwargs)


class RegistrationSummaryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [event_permissions.IsSubRegistrationResponsiblePerson]
    serializer_class = registration_serializers.RegistrationSummarySerializer

    def get_queryset(self) -> QuerySet:
        registration_id = self.kwargs.get("registration_pk", None)
        return Registration.objects.filter(id=registration_id)


class RegistrationViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = [event_permissions.IsRegistrationResponsiblePerson]
    queryset = Registration.objects.all()

    def create(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        event: event_models.Event = get_object_or_404(event_models.Event, pk=serializer.data['event'])

        scout_organisation_id = serializer.data['scout_organisation']
        err_msg = f'Element (Bund, Ring, Stamm) mit der Id {scout_organisation_id}'
        scout_organisation = custom_get_or_404(
            event_api_exceptions.SomethingNotFound(err_msg),
            basic_models.ScoutHierarchy,
            id=scout_organisation_id
        )
        registration: Registration = Registration(
            scout_organisation=scout_organisation,
            event=event,
        )

        registration.save()
        registration.responsible_persons.add(request.user)

        event_module: QuerySet = event_models.EventModule.objects.filter(event=event.id, required=True)
        # for mapper in event_module:
        #     for attribute_mapper in mapper.attributes.all():
        #         attribute = attribute_mapper.attribute
        #         new_attribute = add_event_attribute(attribute)
        #         registration.tags.add(new_attribute.id)

        json = registration_serializers.RegistrationGetSerializer(registration)
        return Response(json.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs) -> Response:
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        tmp: Registration = serializer.save()

        # tmp.responsible_persons.add(request.user)

        serializer = registration_serializers.RegistrationGetSerializer(tmp)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs) -> Response:
        registration: Registration = self.get_object()
        participants_count = RegistrationParticipant.objects.filter(registration=registration.id).count()
        if participants_count == 0:
            return super().destroy(request, *args, **kwargs)

        if registration.event.last_possible_update < timezone.now():
            raise event_api_exceptions.TooLate
        elif registration.event.registration_deadline < timezone.now():
            raise event_api_exceptions.TooManyParticipants

        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return registration_serializers.RegistrationPostSerializer
        elif self.request.method == 'GET':
            return registration_serializers.RegistrationGetSerializer
        elif self.request.method == 'PUT':
            return registration_serializers.RegistrationPutSerializer
        elif self.request.method == 'DESTROY':
            return registration_serializers.RegistrationPutSerializer


class SimpleRegistrationViewSet(viewsets.ModelViewSet):
    serializer_class = registration_serializers.RegistrationGetSerializer

    def get_queryset(self) -> QuerySet:
        return Registration.objects.all()


class MyRegistrationViewSet(viewsets.ModelViewSet):
    serializer_class = registration_serializers.RegistrationSummarySerializer

    def get_queryset(self) -> QuerySet:
        return Registration.objects.filter(responsible_persons=self.request.user.id)


class RegistrationReadViewSet(viewsets.ModelViewSet):
    serializer_class = registration_serializers.RegistrationReadSerializer

    def get_queryset(self) -> QuerySet:
        return Registration.objects.filter(responsible_persons=self.request.user.id)
