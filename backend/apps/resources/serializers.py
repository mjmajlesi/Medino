from django.urls import reverse
from rest_framework import serializers

from .models import Resource


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
