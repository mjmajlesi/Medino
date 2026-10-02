from django.urls import reverse
from rest_framework import serializers

from apps.academics.models import Lesson

from .models import Resource
from .validators import validate_resource_file


class ResourceSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    lesson_id = serializers.CharField(read_only=True)
    file_url = serializers.SerializerMethodField()
    uploader_name = serializers.SerializerMethodField()

    class Meta:
        model = Resource
        fields = (
            "id",
            "lesson_id",
            "type",
            "title",
            "description",
            "file_url",
            "duration",
            "status",
            "uploader_name",
            "created_at",
        )

    def get_file_url(self, resource):
        if resource.external_url:
            return resource.external_url
        path = reverse("resource-file", args=[resource.pk])
        request = self.context.get("request")
        return request.build_absolute_uri(path) if request else path

    def get_uploader_name(self, resource):
        if resource.uploaded_by:
            name = resource.uploaded_by.get_full_name().strip()
            if name:
                return name
        return "مدینو"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not data["description"]:
            data.pop("description")
        if not data["duration"]:
            data.pop("duration")
        return data


class ResourceUploadSerializer(serializers.ModelSerializer):
    lesson = serializers.PrimaryKeyRelatedField(queryset=Lesson.objects.select_related("professor"))
    professor = serializers.CharField(required=False, write_only=True)
    file = serializers.FileField(required=False)
    external_url = serializers.URLField(required=False, allow_blank=True)

    class Meta:
        model = Resource
        fields = ("lesson", "professor", "type", "title", "description", "file", "external_url")

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("A title is required.")
        return value

    def validate_external_url(self, value):
        if value and not value.startswith(("https://", "http://")):
            raise serializers.ValidationError("Use an HTTP or HTTPS URL.")
        return value

    def validate(self, attrs):
        professor = attrs.pop("professor", None)
        if professor is not None and professor.strip() != attrs["lesson"].professor.name:
            raise serializers.ValidationError(
                {"professor": "Professor does not match the selected lesson."}
            )

        if bool(attrs.get("file")) == bool(attrs.get("external_url")):
            raise serializers.ValidationError(
                {"source": "Provide exactly one source: file or external_url."}
            )
        if attrs.get("file"):
            try:
                validate_resource_file(attrs["file"], attrs["type"])
            except serializers.ValidationError as exc:
                raise serializers.ValidationError({"file": exc.detail}) from exc
        return attrs


class ModerationActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=("approve", "reject"))
