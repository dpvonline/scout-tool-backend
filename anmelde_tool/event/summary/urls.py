from django.urls import include, path
from rest_framework_nested import routers

from anmelde_tool.event.urls import router
from . import views
from .kpi import views as kpi_views

event_summary_router = routers.NestedSimpleRouter(router, r'event', lookup='event')
event_summary_router.register(r'summary', views.EventSummaryViewSet, basename='summary')
event_summary_router.register(r'summary/age-groups', views.EventAgeGroupsSummaryViewSet, basename='age-groups')
event_summary_router.register(r'summary/age-groups-detail', views.EventAgeGroupsSummaryDetailViewSet, basename='age-groups-detail')
event_summary_router.register(r'summary/leader-types', views.EventLeaderTypesSummaryViewSet,
                              basename='leader-types')
event_summary_router.register(r'summary/alcohol-groups', views.EventAlcoholAgeGroupsSummaryViewSet,
                              basename='alcohol-groups')

event_summary_router.register(r'summary/kpi/total-participants', kpi_views.TotalParticipantsViewSet,
                              basename='total-participants')
event_summary_router.register(r'summary/kpi/total-registrations', kpi_views.TotalRegistrationsViewSet,
                              basename='total-registrations')
event_summary_router.register(r'summary/kpi/last-registrations', kpi_views.LastRegistrationsViewSet,
                              basename='last-registrations')
event_summary_router.register(r'summary/kpi/largest-registrations', kpi_views.LargestRegistrationsViewSet,
                              basename='largest-registrations')
event_summary_router.register(r'summary/kpi/booking-options', kpi_views.BookingOptionViewSet,
                              basename='booking-options')
event_summary_router.register(r'summary/registration-by-date', kpi_views.RegistrationByDateViewSet,
                              basename='registration-by-date')
event_summary_router.register(r'summary/participant-locations', views.RegistrationLocationViewSet,
                              basename='participant-locations')
event_summary_router.register(r'summary/event-location', views.EventLocationViewSet, basename='event-location')
event_summary_router.register(r'summary/detailed', views.EventDetailedSummaryViewSet, basename='detailed')
event_summary_router.register(r'summary/parents', views.RegistrationParentViewSet, basename='parents')
event_summary_router.register(r'summary/workshop', views.WorkshopEventSummaryViewSet, basename='workshop')
event_summary_router.register(r'summary/attributes', views.EventModuleSummaryViewSet, basename='attributes')
event_summary_router.register(r'summary/food', views.EventFoodSummaryViewSet, basename='food')
event_summary_router.register(r'summary/cash-list', views.CashSummaryListViewSet, basename='cash-list')
event_summary_router.register(r'summary/merge-registrations', views.MergeRegistrationsViewSet, basename='merge-registrations')
event_summary_router.register(r'summary/cash', views.CashSummaryViewSet, basename='cash')
event_summary_router.register(r'summary/emails/responsible-persons', views.EmailResponsiblePersonsViewSet,
                              basename='emails-responsible-persons')
event_summary_router.register(r'summary/emails/registration-responsible-persons',
                              views.EmailRegistrationResponsiblePersonsViewSet,
                              basename='emails-registration-responsible-persons')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(event_summary_router.urls)),
]
