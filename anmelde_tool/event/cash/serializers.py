from rest_framework import serializers
from django.contrib.auth import get_user_model
from anmelde_tool.event.cash import models as cash_models
from anmelde_tool.registration.serializers import CurrentUserSerializer

User = get_user_model()


class CashIncomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = cash_models.CashIncome
        fields = '__all__'

class CashIncomeReadSerializer(serializers.ModelSerializer):
    transfer_person = CurrentUserSerializer(many=False, read_only=False)
    class Meta:
        model = cash_models.CashIncome
        fields = '__all__'


class MailReminderSerializer(serializers.Serializer):  # noqa
    event_id = serializers.UUIDField()


class MailSingleReminderSerializer(serializers.Serializer):  # noqa
    registration_id = serializers.UUIDField()
