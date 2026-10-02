from rest_framework import serializers

from .models import Lesson, Section
from apps.resources.models import Resource


class SectionSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = Section
        fields = ("id", "slug", "title", "description")


class LessonSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    section_slug = serializers.CharField(source="section.slug", read_only=True)
    professor = serializers.CharField(source="professor.name", read_only=True)

    class Meta:
        model = Lesson
        fields = ("id", "section_slug", "title", "professor", "term", "code")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not data["code"]:
            data.pop("code")
        return data


class LessonFilterSerializer(serializers.Serializer):
    section = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)
    search = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)
    professor = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)
    term = serializers.IntegerField(required=False, min_value=1)
    type = serializers.ChoiceField(required=False, allow_blank=True, choices=Resource.Type.choices)
