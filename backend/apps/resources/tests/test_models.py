from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.academics.models import Lesson, Professor, Section
from apps.resources.models import Resource


class ResourceModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        section = Section.objects.create(slug="basic", title="علوم پایه", order=1)
        professor = Professor.objects.create(name="دکتر رضایی")
        cls.lesson = Lesson.objects.create(
            section=section, professor=professor, title="آناتومی", term=1
        )
        cls.uploader = get_user_model().objects.create_user(
            student_no="400000001", password="strong-password"
        )

    def test_creation_defaults_relationships_and_optional_fields(self):
        resource = Resource.objects.create(
            lesson=self.lesson,
            uploaded_by=self.uploader,
            type=Resource.Type.NOTE,
            title="جزوه آناتومی",
            external_url="https://example.org/anatomy.pdf",
        )
        self.assertEqual(resource.lesson, self.lesson)
        self.assertEqual(resource.uploaded_by, self.uploader)
        self.assertEqual(resource.status, Resource.Status.PENDING)
        self.assertEqual(resource.description, "")
        self.assertEqual(resource.duration, "")
        self.assertEqual(list(self.lesson.resources.all()), [resource])
        self.assertEqual(
            list(Resource.Type.values), ["note", "video", "sample", "summary"]
        )
        self.assertEqual(
            list(Resource.Status.values), ["pending", "approved", "rejected"]
        )

    def test_type_status_title_lesson_and_source_are_validated_on_save(self):
        base = {
            "lesson": self.lesson,
            "type": Resource.Type.NOTE,
            "title": "جزوه آناتومی",
            "external_url": "https://example.org/anatomy.pdf",
        }
        invalid_cases = (
            {"type": "invalid"},
            {"status": "invalid"},
            {"title": "  "},
            {"lesson": None},
            {"external_url": ""},
            {"external_url": "ftp://example.org/anatomy.pdf"},
            {"file": "resources/anatomy.pdf"},
        )
        for override in invalid_cases:
            with self.subTest(override=override), self.assertRaises(ValidationError):
                Resource.objects.create(**{**base, **override})
