from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.academics.models import Lesson, Professor, Section
from apps.resources.models import Resource


class PublicResourceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        section = Section.objects.create(slug="basic", title="علوم پایه", order=1)
        professor = Professor.objects.create(name="دکتر رضایی")
        cls.lesson = Lesson.objects.create(
            section=section, professor=professor, title="آناتومی", term=1
        )
        cls.unpublished_lesson = Lesson.objects.create(
            section=section, professor=professor, title="بیوشیمی", term=1
        )
        cls.uploader = get_user_model().objects.create_user(
            student_no="400000001",
            first_name="علی",
            last_name="مرادی",
            password="strong-password",
        )

    def create_resource(self, *, lesson=None, status=Resource.Status.APPROVED, title="Note"):
        return Resource.objects.create(
            lesson=lesson or self.lesson,
            uploaded_by=self.uploader,
            type=Resource.Type.NOTE,
            title=title,
            status=status,
            external_url="https://example.org/resource.pdf",
        )

    def test_detail_only_returns_approved_resources_without_extra_user_queries(self):
        approved = self.create_resource(title="Approved")
        self.create_resource(status=Resource.Status.PENDING, title="Pending")
        self.create_resource(status=Resource.Status.REJECTED, title="Rejected")

        with self.assertNumQueries(2):
            response = self.client.get(reverse("lesson-detail", args=[self.lesson.pk]))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(set(data), {"lesson", "resources"})
        self.assertEqual(data["lesson"], {
            "id": str(self.lesson.pk),
            "section_slug": "basic",
            "title": "آناتومی",
            "professor": "دکتر رضایی",
            "term": 1,
        })
        self.assertIsInstance(data["resources"], list)
        self.assertEqual([row["id"] for row in data["resources"]], [str(approved.pk)])
        self.assertEqual(data["resources"][0]["uploader_name"], "علی مرادی")

    def test_lesson_with_only_unapproved_resources_returns_empty_array(self):
        self.create_resource(
            lesson=self.unpublished_lesson,
            status=Resource.Status.PENDING,
            title="Unpublished",
        )
        response = self.client.get(reverse("lesson-detail", args=[self.unpublished_lesson.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["resources"], [])

    def test_local_file_is_served_only_when_approved(self):
        with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            approved = Resource.objects.create(
                lesson=self.lesson,
                type=Resource.Type.NOTE,
                title="Approved file",
                status=Resource.Status.APPROVED,
                file=SimpleUploadedFile("note.txt", b"approved content"),
            )
            pending = Resource.objects.create(
                lesson=self.lesson,
                type=Resource.Type.NOTE,
                title="Pending file",
                status=Resource.Status.PENDING,
                file=SimpleUploadedFile("pending.txt", b"private content"),
            )
            response = self.client.get(reverse("resource-file", args=[approved.pk]))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(b"".join(response.streaming_content), b"approved content")
            response.close()
            self.assertEqual(
                self.client.get(reverse("resource-file", args=[pending.pk])).status_code,
                404,
            )
            self.assertEqual(self.client.get("/media/" + pending.file.name).status_code, 404)
