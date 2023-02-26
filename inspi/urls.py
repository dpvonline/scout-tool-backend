# myapi/urls.py
from django.urls import include, re_path, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'tag', views.TagViewSet)
router.register(r'activity', views.ActivityViewSet)
router.register(r'like', views.LikeViewSet)
router.register(r'highscore', views.HighscoreViewSet)
router.register(r'tag-category', views.TagCategoryViewSet)
router.register(r'statistic', views.StatisticViewSet)
router.register(r'material-item', views.MaterialItemViewSet)
router.register(r'material-unit', views.MaterialUnitViewSet)
router.register(r'material-name', views.MaterialNameViewSet)
router.register(r'experiment', views.ExperimentViewSet)
router.register(r'experiment-overview', views.ExperimentOverviewViewSet)
router.register(r'experiment-item', views.ExperimentItemViewSet)
router.register(r'random-activity', views.RandomActivityViewSet)
router.register(r'top-views', views.TopViewsViewSet)
router.register(r'admin-activity', views.AdminActivityViewSet)
router.register(r'activity-timestamp', views.ActivityTimestampViewSet)
router.register(r'image-meta', views.ImageMetaViewSet)
router.register(r'next-best-heimabend', views.NextBestHeimabendViewSet)
router.register(r'activity-of-the-week', views.ActivityOfTheWeekViewSet)
router.register(r'admin-sitemap', views.ActivitySitemapViewSet)
router.register(r'activity-publish', views.ChangePublishStatusViewSet, basename='activity-publish')
router.register(r'material-items', views.MaterialItemsViewSet, basename='material-items')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path(r'', include(router.urls)),
    re_path(r'^upload/$', views.ImageViewSet.as_view({'get': 'list'}), name='file-upload')
]
