from django.contrib import admin
from django.urls import path, include
from . import index

urlpatterns = [
    # path('', index.RedirectView.as_view()),
    path('admin/', admin.site.urls),
    path('basic/', include('basic.urls')),
    path('auth/', include('authentication.urls')),
    path('event/', include('anmelde_tool.event.urls')),
    path('message/', include('messaging.urls')),
    path('food/', include('food.urls')),
    path('keycloak/', include('keycloak_auth.urls')),
    path('inspi/', include('inspi.urls')),
]
