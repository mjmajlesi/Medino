from rest_framework import serializers

from .models import Lesson, Professor, Section
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
        fields = ("id", "section_slug", "title", "professor", "term", "code", "views", "created_at")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not data["code"]:
            data.pop("code")
        return data


class LessonWriteSerializer(serializers.ModelSerializer):
    section_slug = serializers.SlugRelatedField(
        source="section",
        slug_field="slug",
        queryset=Section.objects.all(),
        error_messages={"does_not_exist": "Section does not exist."},
    )
    professor = serializers.CharField(max_length=150, trim_whitespace=True)
    title = serializers.CharField(max_length=200, trim_whitespace=True)
    code = serializers.CharField(max_length=32, required=False, allow_blank=True)

    class Meta:
        model = Lesson
        fields = ("section_slug", "title", "professor", "term", "code")

    def validate_professor(self, name):
        matches = list(Professor.objects.filter(name=name).order_by("pk")[:2])
        if not matches:
            raise serializers.ValidationError("Professor does not exist.")
        if len(matches) > 1:
            raise serializers.ValidationError("Professor name is ambiguous.")
        return matches[0]

    def validate_term(self, value):
        if value < 1:
            raise serializers.ValidationError("Term must be positive.")
        return value

    def update(self, instance, validated_data):
        # PUT replaces the optional code as well as the required fields.
        validated_data.setdefault("code", "")
        return super().update(instance, validated_data)


class LessonFilterSerializer(serializers.Serializer):
    section = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)
    search = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)
    professor = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)
    term = serializers.IntegerField(required=False, min_value=1)
    type = serializers.ChoiceField(required=False, allow_blank=True, choices=Resource.Type.choices)
    ordering = serializers.ChoiceField(required=False, choices=("-created_at", "-views"))
