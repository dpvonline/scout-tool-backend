import re

import openpyxl
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.forms.models import model_to_dict
from django_filters.rest_framework import DjangoFilterBackend
from keycloak import KeycloakGetError, KeycloakAuthenticationError
from rest_framework import status, viewsets, mixins
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from anmelde_tool.registration.views import create_missing_eat_habits
from authentication import models as auth_models
from authentication import serializers as auth_serializer
from backend.settings import env, keycloak_admin, keycloak_user
from basic.api_exceptions import TooManySearchResults, NoSearchResults, ZipCodeNotFound
from basic.choices import Gender
from basic.helper.choice_to_json import choice_to_json
from basic.helper.get_property_ids import get_zipcode
from basic.models import ScoutHierarchy, ZipCode, EatHabit
from basic.permissions import IsStaffOrReadOnly
from keycloak_auth.helper import (
    REGEX_GROUP,
    check_group_admin_permission,
    get_groups_of_user,
)
from keycloak_auth.models import KeycloakGroup
from keycloak_auth.serializers import FullGroupSerializer
from .choices import BundesPostTextChoice
from .models import EmailNotificationType, CustomUser, Person, RequestGroupAccess
from .serializers import (
    GroupSerializer,
    EmailSettingsSerializer,
    ResponsiblePersonSerializer,
    RegisterSerializer,
    FullUserSerializer,
    EditPersonSerializer,
    UserSerializer,
    PersonSerializer,
    CheckUsernameSerializer,
    StatusRequestGroupGetAccessSerializer,
    CheckEmailSerializer,
    CheckPasswordSerializer,
    MemberSerializer,
    MemberCreateSerializer,
)
from .signals import save_keycloak_user, save_keycloak_person

User: CustomUser = get_user_model()


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50


def clean_str(input):
    if type(input) != str:
        return input
    if input.strip() == "-":
        return None
    return input.strip()


def search_user(request, users):
    search_param = request.GET.get("search")
    if search_param:
        users = users.filter(
            Q(first_name__icontains=search_param)
            | Q(last_name__icontains=search_param)
            | Q(scout_name__icontains=search_param)
        )
    return users


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
            if data[key] is None or data[key] == "":
                del request.data[key]

        if not request.data.get("email"):
            request.data["email"] = request.user.email

        serializer = EditPersonSerializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)

        user_serializer = UserSerializer(data=serializer.data)
        user_serializer.is_valid(raise_exception=True)
        user_data = user_serializer.data

        user_serializer.update(request.user, user_data)
        save_keycloak_user(request.user)

        person_serializer = PersonSerializer(data=serializer.data)
        person_serializer.is_valid(raise_exception=True)
        person_data = person_serializer.data
        person_serializer.update(request.user.person, person_data)

        person_edited = False
        scout_group_id = request.data.get("scout_group")
        if scout_group_id and (
                request.user.person.scout_group is None
                or scout_group_id != request.user.person.scout_group.id
        ):
            scout_group = get_object_or_404(ScoutHierarchy, id=scout_group_id)
            request.user.person.scout_group = scout_group
            person_edited = True
        zip_code_no = request.data.get("zip_code")
        if zip_code_no and (
                request.user.person.zip_code is None
                or zip_code_no != request.user.person.zip_code.id
        ):
            zip_code = ZipCode.objects.filter(zip_code=zip_code_no).first()
            if not zip_code:
                raise ZipCodeNotFound()
            request.user.person.zip_code = zip_code
            person_edited = True

        if request.data.get("eat_habits"):
            request.data["eat_habit"] = request.data.get("eat_habits")
            eat_habits_formatted = create_missing_eat_habits(request)
            del request.data["eat_habit"]

            if eat_habits_formatted and len(eat_habits_formatted) > 0:
                with transaction.atomic():
                    request.user.person.eat_habits.clear()
                    for eat_habit in eat_habits_formatted:
                        eat_habit_id = get_object_or_404(
                            EatHabit, name__iexact=eat_habit
                        ).id
                        request.user.person.eat_habits.add(eat_habit_id)
                person_edited = True

        if person_edited:
            request.user.person.save()
        save_keycloak_person(request.user.person)

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
    search_fields = [
        "user__email",
        "scout_name",
    ]

    def list(self, request, *args, **kwargs) -> Response:

        search_param = request.GET.get("search")
        if search_param:
            queryset = User.objects.filter(
                Q(scout_name__icontains=search_param)
                | Q(user__email__icontains=search_param)
                | Q(scout_organisation__name__icontains=search_param)
            )
        else:
            queryset = User.objects.all()

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


class EmailSettingsViewSet(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
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
        request.data['zip_code'] = get_zipcode(request)
        zip_code_obj = ZipCode.objects.get(id=request.data.get("zip_code"))
        serializers = RegisterSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        try:
            new_keycloak_user_id: str = keycloak_admin.create_user(
                {
                    "email": serializers.data.get("email"),
                    "username": serializers.data.get("username"),
                    "firstName": serializers.data.get("first_name"),
                    "lastName": serializers.data.get("last_name"),
                    "enabled": True,
                    "credentials": [
                        {
                            "value": serializers.data.get("password"),
                            "type": "password",
                        }
                    ],
                    "requiredActions": [
                        "VERIFY_EMAIL",
                    ],
                },
                exist_ok=False,
            )
        except KeycloakGetError as e:
            print(f"Error within registration:\n{e}")
            return Response(
                {"status": "failed", "error": repr(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except KeycloakAuthenticationError as kae:
            print(f"Error within registration:\n{kae}")
            return Response(
                {"status": "failed", "error": repr(kae)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            print(f"Error within registration:\n{e}")
            return Response(
                {"status": "failed", "error": repr(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            new_django_user: CustomUser = User.objects.create_user(
                username=serializers.data.get("username"),
                email=serializers.data.get("email"),
                dsgvo_confirmed=serializers.data.get("dsgvo_confirmed", False),
                email_notification=serializers.data.get(
                    "email_notification", EmailNotificationType.FULL
                ),
                sms_notification=serializers.data.get("sms_notification", True),
                keycloak_id=new_keycloak_user_id,
            )
        except Exception as exception:
            print("failed initialising django user, removing keycloak user")
            print(f"{exception=}")
            keycloak_admin.delete_user(new_keycloak_user_id)
            return Response(
                {"status": "failed", "error": repr(exception)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if serializers.data.get("scout_group"):
            scout_organisation = ScoutHierarchy.objects.get(
                id=serializers.data.get("scout_group")
            )
        else:
            scout_organisation = None

        if new_keycloak_user_id and new_django_user:
            try:
                Person.objects.create(
                    user=new_django_user,
                    scout_name=serializers.data.get("scout_name", ""),
                    first_name=serializers.data.get("first_name", ""),
                    last_name=serializers.data.get("last_name", ""),
                    address=serializers.data.get("address", ""),
                    address_supplement=serializers.data.get("address_supplement", ""),
                    zip_code=zip_code_obj,
                    scout_group=scout_organisation,
                    phone_number=serializers.data.get("phone_number", ""),
                    email=serializers.data.get("email"),
                    bundespost=serializers.data.get("bundespost", ""),
                    birthday=serializers.data.get("birthday"),
                    gender=serializers.data.get("gender", ""),
                    leader=serializers.data.get("leader", ""),
                    scout_level=serializers.data.get("scout_level", ""),
                )
            except Exception as exception:
                print(
                    "failed initialising django person model, removing keycloak and django user"
                )
                print(f"{exception=}")
                # when django user is deleted, keycloak user is deleted as well
                new_django_user.delete()
                return Response(
                    {"status": "failed", "error": repr(exception)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        verify_mail = keycloak_admin.send_verify_email(
            user_id=new_keycloak_user_id,
            client_id=env("KEYCLOAK_ADMIN_USER"),
            redirect_uri=env("FRONT_URL"),
        )

        if scout_organisation and scout_organisation.keycloak:
            try:
                request_group_access = RequestGroupAccess.objects.create(
                    user=new_django_user,
                    group=scout_organisation.keycloak,
                )
            except Exception as exception:
                print("failed requesting group access")
                print(f"{exception=}")

        return Response("ok", status=status.HTTP_200_OK)


class MyOwnRequestGroupAccessViewSet(
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    serializer_class = StatusRequestGroupGetAccessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RequestGroupAccess.objects.filter(user=self.request.user)


class MyDecidableRequestGroupAccessViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet
):
    serializer_class = StatusRequestGroupGetAccessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return RequestGroupAccess.objects.all()
        else:
            keycload_ids = []
            for group in self.request.user.groups.all():
                if check_group_admin_permission(group.name):
                    keycloak_id = REGEX_GROUP.findall(group.name)[0]
                    keycload_ids.append(keycloak_id)
            return RequestGroupAccess.objects.filter(
                group__keycloak_id__in=keycload_ids
            )


class UserGroupViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = FullGroupSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]

    def get_queryset(self):
        token = self.request.META.get("HTTP_AUTHORIZATION")
        ids = get_groups_of_user(token, self.request.user.keycloak_id)
        return KeycloakGroup.objects.filter(keycloak_id__in=ids)

    def list(self, request, *args, **kwargs) -> Response:
        groups = self.get_queryset()
        serializer = FullGroupSerializer(
            groups, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserPermissionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request) -> Response:
        composite_client_roles = keycloak_admin.get_composite_client_roles_of_user(
            request.user.keycloak_id,
            keycloak_admin.realm_management_client_id,
            brief_representation=True,
        )
        ids = [val["name"] for val in composite_client_roles]
        return Response(ids, status=status.HTTP_200_OK)


def find_user(value, keycloak_param, *filter_args, **filter_kwargs):
    if User.objects.filter(*filter_args, **filter_kwargs).exists():
        return True

    keycloak_users = keycloak_admin.get_users({keycloak_param: value})
    if keycloak_users:
        for user in keycloak_users:
            if value == user[keycloak_param]:
                return True

    return False


class CheckUsername(viewsets.ViewSet):
    def create(self, request, *args, **kwargs) -> Response:
        serializer = CheckUsernameSerializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        name = serializer.data["username"]

        if not name.isalnum():
            return Response(
                "Der Username darf keine Sonderzeichen enthalten.",
                status=status.HTTP_400_BAD_REQUEST,
            )

        if re.search("[äöüÄÖÜß ]", name):
            return Response(
                "Der Username darf keine Umlaute enthalten.",
                status=status.HTTP_400_BAD_REQUEST,
            )

        found = find_user(name, "username", username__iexact=name)
        if found:
            return Response(
                "Username ist bereits in Benutzung.", status=status.HTTP_409_CONFLICT
            )
        return Response("Username ist frei.", status=status.HTTP_200_OK)


class CheckEmail(viewsets.ViewSet):
    def create(self, request, *args, **kwargs) -> Response:
        serializer = CheckEmailSerializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        email = serializer.data["email"]

        found = find_user(email, "email", email__iexact=email)

        if found:
            return Response(
                "Email ist bereits in Benutzung.", status=status.HTTP_409_CONFLICT
            )
        return Response("Email ist frei.", status=status.HTTP_200_OK)


class CheckPassword(viewsets.ViewSet):
    def create(self, request, *args, **kwargs) -> Response:
        serializer = CheckPasswordSerializer(data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        password = serializer.data["password"]

        if bool(re.search(r" ", password)):
            return Response(
                "Das Passwort darf kein Leerzeichen enthalten.",
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(password) < 8:
            return Response(
                "Das Passwort muss mindestens 8 Zeichen enthalten.",
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not bool(re.search(r"\d", password)):
            return Response(
                "Das Passwort muss mindestens eine Zahl enthalten.",
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not re.search("[!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~ ]", password):
            return Response(
                "Das Passwort muss mindestens ein Sonderzeichen enthalten.",
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not any(x.isupper() for x in password):
            return Response(
                "Das Passwort muss mindestens einen Großbuchstaben enthalten.",
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not any(x.islower() for x in password):
            return Response(
                "Das Passwort muss mindestens einen Kleinbuchstaben enthalten.",
                status=status.HTTP_400_BAD_REQUEST,
            )

        if re.match(r"[^@]+@[^@]+\.[^@]+", password):
            return Response(
                "Das Passwort darf keine Email Adresse sein.",
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response("Passwort ist gültig.", status=status.HTTP_200_OK)


class MyMembersViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MemberSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        token = self.request.META.get("HTTP_AUTHORIZATION")
        scout_group = self.request.user.person.scout_group

        if not scout_group or not scout_group.keycloak:
            return Person.objects.none()

        group_id = scout_group.keycloak.keycloak_id

        all_users = True
        try:
            keycloak_user.get_group_users(token, group_id)
        except KeycloakGetError:
            all_users = False

        if all_users:
            users = Person.objects.filter(
                Q(scout_group=scout_group) | Q(created_by=self.request.user)
            ).select_related("user", "scout_group", "zip_code")
        else:
            users = Person.objects.filter(
                created_by=self.request.user
            ).select_related("user", "scout_group", "zip_code")

        user = search_user(self.request, users)
        return user

    def get_serializer_class(self):
        if self.action == "create" or self.action == "update":
            return EditPersonSerializer
        else:
            return MemberSerializer


class MyMembersUploadViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MemberSerializer

    def create(self, request, *args, **kwargs) -> Response:
        token = self.request.META.get("HTTP_AUTHORIZATION")
        scout_group = request.user.person.scout_group

        if not scout_group or not scout_group.keycloak:
            return Response(
                {"status": "Du hast keinen gültigen Stamm", "verified": False},
                status=status.HTTP_200_OK,
            )

        file = request.FILES["file"]
        if not file.name.endswith(".xlsx"):
            return Response(
                {"status": "Falsches Dateiformat", "verified": False},
                status=status.HTTP_200_OK,
            )

        wb = openpyxl.load_workbook(file, read_only=True)
        first_sheet = wb.get_sheet_names()[0]
        ws = wb.get_sheet_by_name(first_sheet)
        data = []
        success_count = 0
        data_count = 0
        report = []
        response_data = []

        for row in ws.iter_rows(min_row=4, max_col=11, max_row=154):
            if clean_str(row[2].value) == "" or not row[2].value:
                continue
            data_line = {}
            data_line["scout_name"] = clean_str(row[1].value)  # B
            data_line["first_name"] = clean_str(row[2].value)  # C
            data_line["last_name"] = clean_str(row[3].value)  # D
            data_line["address"] = clean_str(row[4].value)  # E
            data_line["zip_code"] = clean_str(str(int(row[5].value)))  # F
            data_line["gender"] = clean_str(row[6].value)  # G
            data_line["birthday"] = clean_str(row[7].value)  # H
            data_line["eat_habit_1"] = clean_str(row[8].value)  # I
            data_line["eat_habit_2"] = clean_str(row[9].value)  # J
            data_line["eat_habit_3"] = clean_str(row[10].value)  # K
            data.append(data_line)
            data_count += 1

        for item in data:
            if Person.objects.filter(
                    first_name=item["first_name"],
                    last_name=item["last_name"],
                    birthday=item["birthday"],
                    scout_group=scout_group
            ).exists():
                report.append(
                    f"{item['first_name']} {item['last_name']} {item['birthday'].date()} ist bereits vorhanden"
                )
                continue

            gender_value = None
            # handle gender
            for gender in Gender.choices:
                if data_line["gender"] == gender[1]:
                    gender_value = gender[0]

            # handle zip_code
            zip_code = ZipCode.objects.filter(zip_code=item["zip_code"]).first()

            person_obj = Person.objects.create(
                scout_name=item["scout_name"],
                first_name=item["first_name"],
                last_name=item["last_name"],
                address=item["address"],
                birthday=item["birthday"],
                gender=gender_value,
                scout_group=scout_group,
                zip_code=zip_code
            )
            # handle created_by
            person_obj.created_by.add(request.user)

            # handle eat_habits
            eat_habit_list = []
            if item["eat_habit_1"]:
                eat_habit_list.append(item["eat_habit_1"])
            if item["eat_habit_2"]:
                eat_habit_list.append(item["eat_habit_2"])
            if item["eat_habit_3"]:
                eat_habit_list.append(item["eat_habit_3"])

            if eat_habit_list:
                for eat_habit in eat_habit_list:
                    try:
                        eat_habit = get_object_or_404(EatHabit, name__iexact=eat_habit)
                        person_obj.eat_habits.add(eat_habit)
                        person_obj.save()
                    except:
                        pass

            dict_model = model_to_dict(
                person_obj, fields=[field.name for field in person_obj._meta.fields]
            )

            dict_model["birthday"] = dict_model["birthday"].date()
            success_count += 1
            response_data.append(dict_model)

        serializer = MemberCreateSerializer(data=response_data, many=True)
        serializer.is_valid(raise_exception=True)

        return Response(
            {
                "status": serializer.data,
                "report": report,
                "success_count": success_count,
                "total_count": len(data),
            },
            status=status.HTTP_200_OK,
        )


class MyTribeVerifiedViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request) -> Response:
        user: CustomUser = self.request.user
        if not user.person.scout_group or not user.person.scout_group.keycloak:
            return Response(
                {"status": "Du hast keinen gültigen Stamm", "verified": False},
                status=status.HTTP_200_OK,
            )

        group_id = user.person.scout_group.keycloak.keycloak_id
        token = self.request.META.get("HTTP_AUTHORIZATION")

        try:
            keycloak_user.get_group_users(token, group_id)
        except KeycloakGetError:
            return Response(
                {
                    "status": "Du bist nicht berechtigt auf diesen Stamm zuzugreifen. Bitte deine Stammesführung dich zu authorisieren.",
                    "verified": False,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "status": "Dein Stammesführer hat dich erfolgreich verifiziert",
                "verified": True,
            },
            status=status.HTTP_200_OK,
        )


class AddablePersons(viewsets.ModelViewSet):
    serializer_class = auth_serializer.MemberSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]

    def get_queryset(self):
        token = self.request.META.get("HTTP_AUTHORIZATION")
        scout_group = self.request.user.person.scout_group

        if not scout_group or not scout_group.keycloak:
            return auth_models.Person.objects.none()

        group_id = scout_group.keycloak.keycloak_id

        all_users = True
        try:
            keycloak_user.get_group_users(token, group_id)
        except KeycloakGetError:
            all_users = False

        if all_users:
            users = Person.objects.filter(
                Q(scout_group=scout_group) | Q(created_by=self.request.user)
            ).select_related("user", "scout_group", "zip_code")
        else:
            users = Person.objects.filter(
                created_by=self.request.user
            ).select_related("user", "scout_group", "zip_code")

        registration_id = self.request.query_params.get("registration_id", None)

        # todo: filter for already registered persons
        # registered_person = RegistrationParticipant.objects.all().values_list(
        #     "person", flat=True
        # )

        return search_user(self.request, users)
