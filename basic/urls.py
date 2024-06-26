from django.urls import include, path
from rest_framework_nested import routers

from . import views

router = routers.SimpleRouter()
router.register(r'scout-hierarchy', views.ScoutHierarchyViewSet, basename='scout-hierarchy')
router.register(r'scout-hierarchy-detail', views.ScoutHierarchyDetailedViewSet)
router.register(r'zip-code', views.ZipCodeViewSet)
router.register(r'check-zip-code', views.CheckZipCodeViewSet,
                basename='check-zip-code')
router.register(r'tags', views.TagViewSet)
router.register(r'tag-types', views.TagTypeViewSet)
router.register(r'eat-habits', views.EatHabitViewSet)
router.register(r'theme', views.FrontendThemeViewSet)
router.register(r'scout-orga-level', views.ScoutOrgaLevelViewSet)
router.register(r'gender', views.GenderViewSet, basename='gender')

router.register(r'search', views.SearchViewSet, basename='search')

router.register(r'faq', views.DescriptionViewSet, basename='faq')
router.register(r'privacy', views.DescriptionViewSet, basename='privacy')

urlpatterns = [
    path('', include(router.urls)),
    # path("graphql", GraphQLView.as_view(graphiql=True)),
]
