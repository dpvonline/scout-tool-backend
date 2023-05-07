from django.urls import include, path
from rest_framework_nested import routers

from anmelde_tool.email_services import views as email_services_views
from anmelde_tool.attributes import views as attributes_views
from . import views

router = routers.SimpleRouter()
router.register(r'event-location', views.EventLocationViewSet)
router.register(r'event', views.EventViewSet, basename='event')
router.register(r'my-invitations', views.MyInvitationsViewSet, basename='my-invitations')
router.register(r'event-overview', views.EventOverviewViewSet, basename='event-overview')
router.register(r'event-read', views.EventReadViewSet)
router.register(r'email-sets', email_services_views.StandardEmailViewSet)
router.register(r'travel-type-choices', attributes_views.TravelTypeViewSet, basename='travel-type-choices')

event_router = routers.NestedSimpleRouter(router, r'event', lookup='event')
event_router.register(r'booking-options', views.BookingOptionViewSet, basename='booking-options')
event_router.register(r'assigned-event-modules', views.AssignedEventModulesViewSet, basename='assigned-event-modules')
event_router.register(r'available-modules', views.AvailableEventModulesViewSet, basename='available-modules')

# event_module_router.register(r'attribute-mapper', views.EventModuleAttributeMapperViewSet,basename='attribute-mapper')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('', include(event_router.urls)),
    path('', include('anmelde_tool.registration.urls')),
    path('', include('anmelde_tool.event.summary.urls')),
    path('choices/', include('anmelde_tool.event.choices.urls')),
    path('cash/', include('anmelde_tool.event.cash.urls')),
    path('', include('anmelde_tool.event.file_generator.urls')),
    path('', include('anmelde_tool.event.email.urls')),
    path('', include('anmelde_tool.attributes.urls'))
]
