from django.db.models import Q, QuerySet
from django_filters import CharFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import viewsets, status
from rest_framework.exceptions import NotFound
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from basic import models as basic_models
from basic import serializers as basic_serializers
from basic.api_exceptions import TooManySearchResults, NoSearchResults, NoSearchValue
from basic.choices import Gender, DescriptionType
from basic.helper.choice_to_json import choice_to_json
from basic.permissions import IsStaffOrReadOnly
from keycloak_auth import models as keycloak_models
from keycloak_auth import serializers as keycloak_serializers
from messaging import models as messaging_models
from messaging import serializers as messaging_serializers


class ScoutHierarchyViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsStaffOrReadOnly]
    queryset = basic_models.ScoutHierarchy.objects.all().exclude(level=6)
    serializer_class = basic_serializers.ScoutHierarchySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['level']


class ScoutHierarchyDetailedViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsStaffOrReadOnly]
    queryset = basic_models.ScoutHierarchy.objects.all().exclude(level=6)
    serializer_class = basic_serializers.ScoutHierarchyDetailedSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['level']


class ScoutOrgaLevelViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsStaffOrReadOnly]
    queryset = basic_models.ScoutOrgaLevel.objects.all()
    serializer_class = basic_serializers.ScoutOrgaLevelSerializer


class ZipCodeSearchFilter(FilterSet):
    zip_city = CharFilter(field_name='zip_city', method='get_zip_city')

    class Meta:
        model = basic_models.ZipCode
        fields = ['zip_code', 'city', 'id']

    def get_zip_city(self, queryset, field_name, value) -> QuerySet[basic_models.ZipCode]:
        if value is None:
            raise NoSearchValue
        cities = queryset.filter(
            Q(zip_code__contains=value) | Q(city__icontains=value))
        if cities.count() > 250:
            raise TooManySearchResults
        if cities.count() == 0:
            raise NoSearchResults
        return cities


class ZipCodeViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsStaffOrReadOnly]
    queryset = basic_models.ZipCode.objects.all()
    serializer_class = basic_serializers.ZipCodeSerializer
    filterset_class = ZipCodeSearchFilter


def find_zip_code(value, keycloak_param, *filter_args, **filter_kwargs):
    if basic_models.ZipCode.objects.filter(*filter_args, **filter_kwargs).exists():
        return True

    return False


class CheckZipCodeViewSet(viewsets.ReadOnlyModelViewSet):
    def create(self, request, *args, **kwargs) -> Response:
        serializer = basic_serializers.CheckZipCodeSerializer(
            data=request.data, many=False)
        serializer.is_valid(raise_exception=True)
        zip_code = serializer.data['zip_code']

        found = find_zip_code(zip_code, 'zip_code', zip_code__iexact=zip_code)

        if found:
            return Response('Zip Code ist vorhanden.', status=status.HTTP_200_OK)

        return Response('Zip Code nicht vorhanden.', status=status.HTTP_409_CONFLICT)


class TagViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly]
    queryset = basic_models.Tag.objects.all()
    serializer_class = basic_serializers.TagShortSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['type', 'type__name']
    search_fields = ['type__name', 'name']


class TagTypeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStaffOrReadOnly]
    queryset = basic_models.TagType.objects.all()
    serializer_class = basic_serializers.TagTypeShortSerializer
    filter_backends = [SearchFilter, ]
    search_fields = ['name', ]
    ordering_fields = ['id', ]


class DescriptionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsStaffOrReadOnly]
    serializer_class = basic_serializers.DescriptionSerializer

    def get_queryset(self) -> QuerySet:
        if self.basename == 'faq':
            return basic_models.Description.objects.filter(public=True, type=DescriptionType.FAQ)
        elif self.basename == 'privacy':
            return basic_models.Description.objects.filter(public=True, type=DescriptionType.Privacy)
        else:
            raise NotFound


class EatHabitViewSet(viewsets.ModelViewSet):
    queryset = basic_models.EatHabit.objects.all()
    serializer_class = basic_serializers.EatHabitSerializer
    permission_classes = [IsStaffOrReadOnly]


class FrontendThemeViewSet(viewsets.ModelViewSet):
    queryset = basic_models.FrontendTheme.objects.all()
    serializer_class = basic_serializers.FrontendThemeSerializer
    permission_classes = [IsAuthenticated]


class GenderViewSet(viewsets.ViewSet):

    def list(self, request) -> Response:
        result = choice_to_json(Gender.choices)
        return Response(result, status=status.HTTP_200_OK)


class SearchViewSet(viewsets.ViewSet):

    def list(self, request) -> Response:
        query = request.GET.get("query", None)

        groups = keycloak_models.KeycloakGroup.objects.all()
        # users = authentication_models.CustomUser.objects.all()
        issues = messaging_models.Issue.objects.all()

        if query:
            groups = groups.filter(name__icontains=query)
            # users = users.filter(name__icontains=query)
            issues = issues.filter(issue_subject__icontains=query)

            return_groups = keycloak_serializers.FullGroupSerializer(
                groups, many=True).data
            # return_users = authentication_serializers.UserShortSerializer(users, many=True).data
            return_issues = messaging_serializers.IssueSerializer(
                issues, many=True).data

            return Response({
                "group": return_groups,
                # "user": return_users,
                "issue": return_issues,
            })
        return Response({
            "group": [],
            "issue": [],
        })
