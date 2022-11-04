from django.contrib.auth import get_user_model
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from keycloak import KeycloakGetError, KeycloakAuthenticationError
from rest_framework import status, viewsets, mixins
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.settings import env, keycloak_admin
from basic.api_exceptions import TooManySearchResults, NoSearchResults
from basic.models import ScoutHierarchy, ZipCode
from basic.permissions import IsStaffOrReadOnly
from .models import EmailNotificationType, CustomUser, Person, RequestGroupAccess
from .serializers import GroupSerializer, EmailSettingsSerializer, ResponsiblePersonSerializer, RegisterSerializer, \
    UserSerializer, RequestGroupAccessSerializer

User: CustomUser = get_user_model()


class PersonalData(viewsets.ViewSet):
    """
    Viewset for handling personal data, contained in the User model
    """
    permission_classes = [IsAuthenticated]

    # pylint: disable=no-self-use
    def list(self, request) -> Response:
        """
        @param request: request information
        @return: Response with serialized user and person data of the user
        """
        serializer = UserSerializer(request.user, many=False)
        return Response(serializer.data)

    # pylint: disable=no-self-use
    def delete(self, request) -> Response:
        """
        @param request: standard django request information
        @return: Statuscode 200 after the user is successfully deleted
        """
        user = request.user
        user.delete()
        return Response(status=status.HTTP_200_OK)

    def update(self, request) -> Response:
        # TODO: add update of user
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)


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
        return Response(EmailNotificationType.choices, status=status.HTTP_200_OK)


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
                    ],
                    'attributes': {
                        'verband': serializers.data.get('scout_organisation'),
                        'fahrtenname': serializers.data.get('scout_name'),
                        'bund': serializers.data.get('scout_organisation'),
                        'stamm': serializers.data.get('scout_organisation'),
                    }
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

        if serializers.data.get('scout_organisation'):
            scout_organisation = ScoutHierarchy.objects.get(id=serializers.data.get('scout_organisation'))
        else:
            scout_organisation = None

        if serializers.data.get('zip_code'):
            zip_code = ZipCode.objects.get(id=serializers.data.get('zip_code'))
        else:
            zip_code = None
        try:
            new_django_user: CustomUser = User.objects.create_user(
                username=serializers.data.get('username'),
                email=serializers.data.get('email'),
                scout_name=serializers.data.get('scout_name', ''),
                scout_organisation=scout_organisation,
                mobile_number=serializers.data.get('mobile_number', ''),
                dsgvo_confirmed=serializers.data.get('dsgvo_confirmed', False),
                email_notification=serializers.data.get('email_notification', EmailNotificationType.FULL),
                sms_notification=serializers.data.get('sms_notification', True),
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

        print(f'{new_django_user=}')

        if new_keycloak_user_id and new_django_user:
            print('all ok, add Person model')

            try:
                Person.objects.create(
                    user=new_django_user,
                    scout_name=serializers.data.get('scout_name', ''),
                    first_name=serializers.data.get('first_name', ''),
                    last_name=serializers.data.get('last_name', ''),
                    address=serializers.data.get('address', ''),
                    address_supplement=serializers.data.get('address_supplement', ''),
                    zip_code=zip_code,
                    scout_group=scout_organisation,
                    phone_number=serializers.data.get('mobile_number', ''),
                    email=serializers.data.get('email'),
                    bundespost=serializers.data.get('bundespost', ''),
                    birthday=serializers.data.get('birth_date'),
                    gender=serializers.data.get('gender', ''),
                    leader=serializers.data.get('leader', ''),
                    scout_level=serializers.data.get('scout_level', '')
                )
            except Exception as exception:
                print('failed initialising django person model,removing keycloak and django user')
                print(f'{exception=}')
                new_django_user.delete()  # when django user is deleted, keycloak user is deleted as well
                return Response(
                    {
                        'status': 'failed',
                        'error': repr(exception)
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        verify_mail = keycloak_admin.send_verify_email(
            user_id=new_keycloak_user_id,
            client_id=env('KEYCLOAK_ADMIN_USER'),
            redirect_uri='http://127.0.0.1:8080/'
        )

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


class RequestGroupAccessViewSet(mixins.RetrieveModelMixin,
                                mixins.UpdateModelMixin,
                                mixins.DestroyModelMixin,
                                mixins.ListModelMixin,
                                GenericViewSet):
    queryset = RequestGroupAccess.objects.all()
    serializer_class = RequestGroupAccessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RequestGroupAccess.objects.filter(user=self.request.user)
