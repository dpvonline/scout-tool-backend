from django.urls import include, path
from rest_framework_nested import routers
from anmelde_tool.registration import views
from anmelde_tool.event.summary import views as event_summary_views

router = routers.SimpleRouter()
router.register('registration', views.RegistrationViewSet, basename='registration')
router.register('registration-read', views.RegistrationReadViewSet, basename='registration-read')
router.register('my-registrations', views.MyRegistrationViewSet, basename='my-registrations')

registration_router = routers.NestedSimpleRouter(router, r'registration', lookup='registration')
registration_router.register(
    r'single-participant', views.RegistrationSingleParticipantViewSet,
    basename='single-participant'
)
registration_router.register(
    r'check-person', views.CheckPersonViewSet,
    basename='check-person'
)
registration_router.register(
    r'registration-rating', views.RegistrationRatingViewSet,
    basename='registration-rating'
)
registration_router.register(r'boolean-attribute', views.RegistrationBooleanAttributeViewSet,
                             basename='boolean-attribute')
registration_router.register(r'string-attribute', views.RegistrationStringAttributeViewSet, basename='string-attribute')
registration_router.register(r'travel-attribute', views.RegistrationTravelAttributeViewSet, basename='travel-attribute')
registration_router.register(r'float-attribute', views.RegistrationFloatAttributeViewSet, basename='float-attribute')
registration_router.register(r'date-time-attribute', views.RegistrationDateTimeAttributeViewSet, basename='date-time-attribute')
registration_router.register(r'integer-attribute', views.RegistrationIntegerAttributeViewSet,
                             basename='integer-attribute')
registration_router.register(r'summary', views.RegistrationSummaryViewSet, basename='summary')
registration_router.register(r'cash-detail', event_summary_views.CashDetailViewSet, basename='cash-detail')

registration_router.register(r'send-confirmation-mail', views.SendConfirmationMail,
                             basename='send-confirmation-mail')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(registration_router.urls)),
]
