from rest_framework import serializers

from anmelde_tool.registration.models import Registration
from basic import serializers as basic_serializers


class RegistrationEventKPISerializer(serializers.ModelSerializer):
    scout_organisation = basic_serializers.ScoutHierarchyDetailedSerializer(many=False, read_only=True)
    count = serializers.IntegerField()

    class Meta:
        model = Registration
        fields = (
            'is_confirmed',
            'is_accepted',
            'scout_organisation',
            'created_at',
            'updated_at',
            'count'
        )
