from django.contrib import admin

from anmelde_tool.workshop.models import Workshop, WorkshopParticipant

admin.site.register(Workshop)
admin.site.register(WorkshopParticipant)
