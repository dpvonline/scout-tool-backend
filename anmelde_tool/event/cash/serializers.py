from rest_framework import serializers
from django.contrib.auth import get_user_model
from anmelde_tool.event.cash import models as cash_models

User = get_user_model()


class CashIncomeSerializer(serializers.ModelSerializer):
    transfer_person = serializers.SlugRelatedField(
        many=False,
        required=False,
        read_only=False,
        slug_field='email',
        queryset=User.objects.all()
    )

    class Meta:
        model = cash_models.CashIncome
        fields = '__all__'


class MailReminderSerializer(serializers.Serializer):  # noqa
    event_id = serializers.UUIDField()
