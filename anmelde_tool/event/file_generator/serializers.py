from rest_framework import serializers

from anmelde_tool.event.file_generator.models import GeneratedFiles, FileTemplate
from anmelde_tool.registration.serializers import CurrentUserSerializer


class FileTemplateSerializer(serializers.ModelSerializer):
    extension = serializers.CharField(source='get_extension_display', read_only=True)
    type = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = FileTemplate
        exclude = ('file',)


class GeneratedFilesGetSerializer(serializers.ModelSerializer):
    user = CurrentUserSerializer(many=False, read_only=True)
    extension = serializers.CharField(source='get_extension_display', read_only=True)
    template = FileTemplateSerializer(many=False, read_only=True)

    class Meta:
        model = GeneratedFiles
        fields = '__all__'


class GeneratedFilesPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedFiles
        fields = (
            'extension',
            'event',
            'user',
            'template',
            'bund'
        )
