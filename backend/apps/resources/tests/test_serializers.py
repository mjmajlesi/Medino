from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIRequestFactory

from apps.academics.models import Lesson, Professor, Section
from apps.resources.models import Resource
from apps.resources.serializers import ResourceSerializer


class ResourceSerializerTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        section = Section.objects.create(slug="basic", title="علوم پایه", order=1)
        professor = Professor.objects.create(name="دکتر رضایی")
        cls.lesson = Lesson.objects.create(
            section=section, professor=professor, title="آناتومی", term=1
        )
        cls.uploader = get_user_model().objects.create_user(
            student_no="400000001",
            first_name="علی",
            last_name="مرادی",
            password="strong-password",
        )

    def test_frontend_fields_types_and_no_internal_details(self):
        resource = Resource.objects.create(
            lesson=self.lesson,
            uploaded_by=self.uploader,
            reviewed_by=self.uploader,
            reviewed_at=timezone.now(),
            type=Resource.Type.VIDEO,
            title="آموزش تصویری آناتومی اندام",
            description="فیلم آموزشی",
            duration="45:00",
            status=Resource.Status.APPROVED,
            external_url="https://example.org/anatomy-video.mp4",
        )
        data = ResourceSerializer(resource).data

        self.assertEqual(
            set(data),
            {
                "id", "lesson_id", "type", "title", "description", "file_url",
                "duration", "status", "uploader_name", "created_at",
            },
        )
        self.assertEqual(data["id"], str(resource.pk))
        self.assertEqual(data["lesson_id"], str(self.lesson.pk))
        self.assertEqual(data["type"], "video")
        self.assertEqual(data["status"], "approved")
        self.assertEqual(data["title"], "آموزش تصویری آناتومی اندام")
        self.assertEqual(data["description"], "فیلم آموزشی")
        self.assertEqual(data["file_url"], "https://example.org/anatomy-video.mp4")
        self.assertEqual(data["duration"], "45:00")
        self.assertEqual(data["uploader_name"], "علی مرادی")
        self.assertIsInstance(datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")), datetime)

    def test_optional_fields_are_omitted_and_missing_uploader_has_safe_name(self):
        resource = Resource.objects.create(
            lesson=self.lesson,
            type=Resource.Type.NOTE,
            title="جزوه آناتومی",
            status=Resource.Status.APPROVED,
            file="resources/anatomy.pdf",
        )
        request = APIRequestFactory().get("http://testserver/api/lessons/1/")
        data = ResourceSerializer(resource, context={"request": request}).data

        self.assertNotIn("description", data)
        self.assertNotIn("duration", data)
        self.assertEqual(data["uploader_name"], "مدینو")
        self.assertEqual(
            data["file_url"],
            f"http://testserver/api/resources/{resource.pk}/file/",
        )
