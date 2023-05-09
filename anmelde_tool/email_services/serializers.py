
from rest_framework import serializers
from . import models

class StandardEmailRegistrationSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.StandardEmailRegistrationSet
        fields = '__all__'