from django.db import connection, transaction
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
        # The professor is resolved after field validation, so check the lesson
        # uniqueness constraint once its database row is known.
        validators = []

    def validate_term(self, value):
        if value < 1:
            raise serializers.ValidationError("Term must be positive.")
        return value

    @staticmethod
    def _resolve_professor(name):
        # Name is not unique in the current schema. Serialize lookups for the
        # same name so concurrent writes cannot create duplicate professors.
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_advisory_xact_lock(73921, hashtext(%s))", [name])
        matches = list(Professor.objects.filter(name=name).order_by("pk")[:2])
        if len(matches) > 1:
            raise serializers.ValidationError({"professor": ["Professor name is ambiguous."]})
        return matches[0] if matches else Professor.objects.create(name=name)

    def _prepare_lesson(self, validated_data, instance=None):
        validated_data["professor"] = self._resolve_professor(validated_data["professor"])
        duplicates = Lesson.objects.filter(
            section=validated_data["section"],
            title=validated_data["title"],
            professor=validated_data["professor"],
            term=validated_data["term"],
        )
        if instance is not None:
            duplicates = duplicates.exclude(pk=instance.pk)
        if duplicates.exists():
            raise serializers.ValidationError(
                {"non_field_errors": [
                    "The fields section_slug, title, professor, term must make a unique set."
                ]}
            )
        return validated_data

    @transaction.atomic
    def create(self, validated_data):
        return super().create(self._prepare_lesson(validated_data))

    @transaction.atomic
    def update(self, instance, validated_data):
        # PUT replaces the optional code as well as the required fields.
        validated_data.setdefault("code", "")
        return super().update(instance, self._prepare_lesson(validated_data, instance))


class LessonFilterSerializer(serializers.Serializer):
    section = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)
    search = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)
    professor = serializers.CharField(required=False, allow_blank=True, trim_whitespace=True)
    term = serializers.IntegerField(required=False, min_value=1)
    type = serializers.ChoiceField(required=False, allow_blank=True, choices=Resource.Type.choices)
    ordering = serializers.ChoiceField(required=False, choices=("-created_at", "-views"))
