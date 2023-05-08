from django.contrib.auth import get_user_model
from rest_framework import serializers

from anmelde_tool.workshop.models import Workshop

User = get_user_model()


class WorkshopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workshop
        fields = '__all__'
