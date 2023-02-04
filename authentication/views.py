import re
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from keycloak import KeycloakGetError, KeycloakAuthenticationError
from rest_framework import status, viewsets, mixins
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from anmelde_tool.event.registration.views import create_missing_eat_habits
from backend.settings import env, keycloak_admin, keycloak_user
from basic.api_exceptions import TooManySearchResults, NoSearchResults
from basic.helper import choice_to_json
from basic.models import ScoutHierarchy, ZipCode, EatHabit
from basic.permissions import IsStaffOrReadOnly
from keycloak_auth.api_exceptions import NotAuthorized
from keycloak_auth.helper import REGEX_GROUP, check_group_admin_permission
from keycloak_auth.models import KeycloakGroup
from keycloak_auth.serializers import FullGroupSerializer
from .choices import BundesPostTextChoice
from .models import EmailNotificationType, CustomUser, Person, RequestGroupAccess
from .serializers import GroupSerializer, EmailSettingsSerializer, ResponsiblePersonSerializer, RegisterSerializer, \
    FullUserSerializer, EditPersonSerializer, UserSerializer, PersonSerializer, \
    CheckUsernameSerializer, StatusRequestGroupGetAccessSerializer, CheckEmailSerializer, CheckPasswordSerializer

User: CustomUser = get_user_model()


class PersonalData(viewsets.ViewSet):
    """
    Viewset for handling personal data, contained in the User model
    """
    permission_classes = [IsAuthenticated]

    # pylint: disable=no-self-use
    def list(self, request, *args, **kwargs) -> Response:
        """
        @param request: request information
        @return: Response with serialized user and person data of the user
        """
        serializer = FullUserSerializer(request.user, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs) -> Response:
        data = dict(request.data)
        for key in data:
            if data[key] is None or data[key] == '':
                del request.data[key]

        if not request.data.get('email'):
            request.data['email'] = request.user.email

        serializer = EditPersonSerializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)

        user_serializer = UserSerializer(data=serializer.data)
        user_serializer.is_valid(raise_exception=True)
        user_data = user_serializer.data

        user_serializer.update(request.user, user_data)

        person_serializer = PersonSerializer(data=serializer.data)
        person_serializer.is_valid(raise_exception=True)
        person_data = person_serializer.data
        person_serializer.update(request.user.person, person_data)

        person_edited = False
        scout_group_id = request.data.get('scout_group')
        if scout_group_id and (
                request.user.person.scout_group is None
                or scout_group_id != request.user.person.scout_group.id):
            scout_group = get_object_or_404(ScoutHierarchy, id=scout_group_id)
            request.user.person.scout_group = scout_group
            person_edited = True
        zip_code_no = request.data.get('zip_code')
        if zip_code_no and (request.user.person.zip_code is None
                            or zip_code_no != request.user.person.zip_code.id):
            zip_code = get_object_or_404(ZipCode, zip_code=zip_code_no)
            request.user.person.zip_code = zip_code
            person_edited = True

        if request.data.get('eat_habits'):
            request.data['eat_habit'] = request.data.get('eat_habits')
            eat_habits_formatted = create_missing_eat_habits(request)
            del request.data['eat_habit']

            if eat_habits_formatted and len(eat_habits_formatted) > 0:
                with transaction.atomic():
                    request.user.person.eat_habits.clear()
                    for eat_habit in eat_habits_formatted:
                        eat_habit_id = get_object_or_404(
                            EatHabit, name__iexact=eat_habit).id
                        request.user.person.eat_habits.add(eat_habit_id)
                person_edited = True

        if person_edited:
            request.user.person.save()

        result = FullUserSerializer(request.user, many=False)
        return Response(result.data, status=status.HTTP_200_OK)

    # pylint: disable=no-self-use
    def delete(self, request, *args, **kwargs) -> Response:
        """
        @param request: standard django request information
        @return: Statuscode 200 after the user is successfully deleted
        """
        user = request.user
        user.delete()
        return Response(status=status.HTTP_200_OK)


class ResponsiblePersonViewSet(viewsets.ModelViewSet):
    """
    Viewset for filtering responsible persons
    """
    permission_classes = [IsStaffOrReadOnly]
    serializer_class = ResponsiblePersonSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['user__email', 'scout_name', ]

    def list(self, request, *args, **kwargs) -> Response:
        queryset = User.objects.all()
        search_param = request.GET.get('search')
        queryset = queryset.filter(
            Q(scout_name__icontains=search_param)
            | Q(user__email__icontains=search_param)
            | Q(scout_organisation__name__icontains=search_param)
        )
        response_len = queryset.count()
        if response_len > 10:
            raise TooManySearchResults
        if response_len == 0:
            raise NoSearchResults

        serializer = ResponsiblePersonSerializer(queryset, many=True)
        return Response(serializer.data)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewset for retrieving groups
    """
    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer

    def get_queryset(self):
        """
        @return: all groups which a user has
        """
        return self.request.user.groups.all()


class EmailSettingsViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    Viewset for retrieving and updating notification settings of a user
    """
    serializer_class = EmailSettingsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        @return: User instance of the user requesting the email settings
        """
        return User.objects.filter(id=self.request.user.id)


class EmailNotificationTypeViewSet(viewsets.ViewSet):
    """
    Viewset for retrieving the choices of notifications
    """
    permission_classes = [IsAuthenticated]

    # pylint: disable=no-self-use
    def list(self, request) -> Response:
        """
        @param request: standard django request
        @return: Response which EmailNotificationType choices
        """
        result = choice_to_json(EmailNotificationType.choices)
        return Response(result, status=status.HTTP_200_OK)


class BundesPostViewSet(viewsets.ViewSet):
    """
    Viewset for retrieving the choices of bundespost
    """
    permission_classes = [IsAuthenticated]

    # pylint: disable=no-self-use
    def list(self, request) -> Response:
        """
        @param request: standard django request
        @return: Response which EmailNotificationType choices
        """
        result = choice_to_json(BundesPostTextChoice.choices)
        return Response(result, status=status.HTTP_200_OK)


class RegisterViewSet(viewsets.ViewSet):

    def create(self, request, *args, **kwargs):
        serializers = RegisterSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        try:
            new_keycloak_user_id: str = keycloak_admin.create_user(
                {
                    'email': serializers.data.get('email'),
                    'username': serializers.data.get('username'),
                    'firstName': serializers.data.get('first_name'),
                    'lastName': serializers.data.get('last_name'),
                    'enabled': True,
                    'credentials': [{
                        'value': serializers.data.get('password'),
                        'type': 'password',
                    }],
                    'requiredActions': [
                        'VERIFY_EMAIL',
                    ]
                }, exist_ok=False
            )
        except KeycloakGetError as e:
            print(f'Error within registration:\n{e}')
            return Response(
                {
                    'status': 'failed',
                    'error': repr(e)
                }, status=status.HTTP_400_BAD_REQUEST
            )
        except KeycloakAuthenticationError as kae:
            print(f'Error within registration:\n{kae}')
            return Response(
                {
                    'status': 'failed',
                    'error': repr(kae)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            print(f'Error within registration:\n{e}')
            return Response(
                {
                    'status': 'failed',
                    'error': repr(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        try:
            new_django_user: CustomUser = User.objects.create_user(
                username=serializers.data.get('username'),
                email=serializers.data.get('email'),
                dsgvo_confirmed=serializers.data.get('dsgvo_confirmed', False),
                email_notification=serializers.data.get(
                    'email_notification', EmailNotificationType.FULL),
                sms_notification=serializers.data.get(
                    'sms_notification', True),
                keycloak_id=new_keycloak_user_id
            )
        except Exception as exception:
            print('failed initialising django user,removing keycloak user')
            print(f'{exception=}')
            keycloak_admin.delete_user(new_keycloak_user_id)
            return Response(
                {
                    'status': 'failed',
                    'error': repr(exception)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        if new_keycloak_user_id and new_django_user:
            try:
                zip_code = None
                if serializers.data.get('zip_code'):
                    zip_code_raw = serializers.data.get('zip_code')
                    zip_code_queryset = ZipCode.objects.filter(
                        zip_code__icontains=zip_code_raw)
                    if zip_code_queryset.count() > 0:
                        zip_code = zip_code_queryset.first()

                Person.objects.create(
                    user=new_django_user,
                    scout_name=serializers.data.get('scout_name', ''),
                    first_name=serializers.data.get('first_name', ''),
                    last_name=serializers.data.get('last_name', ''),
                    address=serializers.data.get('address', ''),
                    address_supplement=serializers.data.get(
                        'address_supplement', ''),
                    zip_code=zip_code,
                    scout_group=ScoutHierarchy.objects.get(id = serializers.data.get('scout_group')),
                    phone_number=serializers.data.get('phone_number', ''),
                    email=serializers.data.get('email'),
                    bundespost=serializers.data.get('bundespost', ''),
                    birthday=serializers.data.get('birthday'),
                    gender=serializers.data.get('gender', ''),
                    leader=serializers.data.get('leader', ''),
                    scout_level=serializers.data.get('scout_level', '')
                )
            except Exception as exception:
                print(
                    'failed initialising django person model,removing keycloak and django user')
                print(f'{exception=}')
                # when django user is deleted, keycloak user is deleted as well
                new_django_user.delete()
                return Response(
                    {
                        'status': 'failed',
                        'error': repr(exception)
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        verify_mail = keycloak_admin.send_verify_email(
            user_id=new_keycloak_user_id,
            client_id=env('KEYCLOAK_ADMIN_USER'),
            redirect_uri=env('FRONT_URL')
        )

        if serializers.data.get('scout_organisation'):
            scout_organisation = serializers.data.get('scout_organisation')
        else:
            scout_organisation = None
        if scout_organisation and scout_organisation.keycloak:
            try:
                request_group_access = RequestGroupAccess.objects.create(
                    user=new_django_user,
                    group=scout_organisation.keycloak,
                )
            except Exception as exception:
                print('failed requesting group access')
                print(f'{exception=}')

        return Response('ok', status=status.HTTP_200_OK)


class MyOwnRequestGroupAccessViewSet(
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    serializer_class = StatusRequestGroupGetAccessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RequestGroupAccess.objects.filter(user=self.request.user)


class MyDecidableRequestGroupAccessViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    serializer_class = StatusRequestGroupGetAccessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        keycload_ids = []
        for group in self.request.user.groups.all():
            if check_group_admin_permission(group.name):
                keycloak_id = REGEX_GROUP.findall(group.name)[0]
                keycload_ids.append(keycloak_id)

        return RequestGroupAccess.objects.filter(group__keycloak_id__in=keycload_ids)


class UserGroupViewSet(mixins.ListModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        token = self.request.META.get('HTTP_AUTHORIZATION')
        try:
            # keycloak_groups = keycloak_user.get_user_groups(
            #     token,
            #     self.request.user.keycloak_id,
            #     brief_representation=True
            #     )
            keycloak_groups = keycloak_admin.get_user_groups(
                self.request.user.keycloak_id,
                brief_representation=True
            )
        except KeycloakGetError:
            raise NotAuthorized()

        ids = [val['id'] for val in keycloak_groups]
        return KeycloakGroup.objects.filter(keycloak_id__in=ids)

    def list(self, request, *args, **kwargs) -> Response:
        groups = self.get_queryset()
        serializer = FullGroupSerializer(
            groups, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserPermissionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request) -> Response:
        composite_client_roles = keycloak_admin.get_composite_client_roles_of_user(
            request.user.keycloak_id,
            keycloak_admin.realm_management_client_id,
            brief_representation=True
        )
        ids = [val['name'] for val in composite_client_roles]
        return Response(ids, status=status.HTTP_200_OK)


def find_user(value, keycloak_param, *filter_args, **filter_kwargs):
    found = False
    if User.objects.filter(*filter_args, **filter_kwargs).exists():
        found = True

    keycloak_users = keycloak_admin.get_users({keycloak_param: value})
    if keycloak_users:
        for user in keycloak_users:
            if value == user[keycloak_param]:
                found = True
                break
    return found


class CheckUsername(viewsets.ViewSet):

    def create(self, request, *args, **kwargs) -> Response:
        serializer = CheckUsernameSerializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        name = serializer.data['username']

        if not name.isalnum():
            return Response('Der Username darf keine Sonderzeichen enthalten.', status=status.HTTP_400_BAD_REQUEST)

        if re.search("[äöüÄÖÜß ]", name):
            return Response('Der Username darf keine Umlaute enthalten.', status=status.HTTP_400_BAD_REQUEST)

        found = find_user(name, 'username', username__iexact=name)
        if found:
            return Response('Username ist bereits in Benutzung.', status=status.HTTP_409_CONFLICT)
        return Response('Username ist frei.', status=status.HTTP_200_OK)


class CheckEmail(viewsets.ViewSet):

    def create(self, request, *args, **kwargs) -> Response:
        serializer = CheckEmailSerializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        email = serializer.data['email']

        found = find_user(email, 'email', email__iexact=email)

        if found:
            return Response('Email ist bereits in Benutzung.', status=status.HTTP_409_CONFLICT)
        return Response('Email ist frei.', status=status.HTTP_200_OK)


class CheckPassword(viewsets.ViewSet):

    def create(self, request, *args, **kwargs) -> Response:
        serializer = CheckPasswordSerializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        password = serializer.data['password']

        if bool(re.search(r' ', password)):
            return Response('Das Passwort darf kein Leerzeichen enthalten.', status=status.HTTP_400_BAD_REQUEST)

        if len(password) < 8:
            return Response('Das Passwort muss mindestens 8 Zeichen enthalten.', status=status.HTTP_400_BAD_REQUEST)

        if not bool(re.search(r'\d', password)):
            return Response(
                'Das Passwort muss mindestens eine Zahl enthalten.',
                status=status.HTTP_400_BAD_REQUEST
            )

        if not re.search("[!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~ ]", password):
            return Response(
                'Das Passwort muss mindestens ein Sonderzeichen enthalten.',
                status=status.HTTP_400_BAD_REQUEST
            )

        if not any(x.isupper() for x in password):
            return Response(
                'Das Passwort muss mindestens einen Großbuchstaben enthalten.',
                status=status.HTTP_400_BAD_REQUEST
            )

        if not any(x.islower() for x in password):
            return Response(
                'Das Passwort muss mindestens einen Kleinbuchstaben enthalten.',
                status=status.HTTP_400_BAD_REQUEST
            )

        if re.match(r'[^@]+@[^@]+\.[^@]+', password):
            return Response(
                'Das Passwort darf keine Email Adresse sein.',
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response('Passwort ist gültig.', status=status.HTTP_200_OK)
