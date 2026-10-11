import os
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.academics.models import Lesson, Professor, Section
from apps.academics.serializers import LessonSerializer
from apps.resources.models import Resource


User = get_user_model()


class LessonManagementAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.basic = Section.objects.create(slug="basic", title="Basic", order=1)
        cls.clinical = Section.objects.create(slug="clinical", title="Clinical", order=2)
        cls.professor = Professor.objects.create(name="Dr. Example")
        cls.other_professor = Professor.objects.create(name="Dr. Other")
        cls.lesson = Lesson.objects.create(
            section=cls.basic,
            professor=cls.professor,
            title="Existing Anatomy",
            term=1,
            code="OLD-101",
            views=7,
        )
        cls.other_lesson = Lesson.objects.create(
            section=cls.clinical,
            professor=cls.other_professor,
            title="Other Lesson",
            term=3,
        )
        cls.student = User.objects.create_user(student_no="student", password="StrongPass!2026")
        cls.staff = User.objects.create_user(
            student_no="staff", password="StrongPass!2026", is_staff=True
        )
        cls.superuser = User.objects.create_superuser(
            student_no="superuser", password="StrongPass!2026"
        )

    def setUp(self):
        self.client = APIClient()
        self.list_url = reverse("lesson-list")
        self.detail_url = reverse("lesson-detail", args=[self.lesson.pk])
        self.payload = {
            "section_slug": "basic",
            "title": "Anatomy",
            "professor": "Dr. Example",
            "term": 2,
            "code": "ANAT-101",
        }

    def authenticate(self, user):
        token = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_anonymous_write_methods_require_authentication(self):
        responses = (
            self.client.post(self.list_url, self.payload, format="json"),
            self.client.put(self.detail_url, self.payload, format="json"),
            self.client.delete(self.detail_url),
        )
        self.assertEqual([response.status_code for response in responses], [401, 401, 401])

    def test_student_write_methods_are_forbidden(self):
        self.authenticate(self.student)
        responses = (
            self.client.post(self.list_url, self.payload, format="json"),
            self.client.put(self.detail_url, self.payload, format="json"),
            self.client.delete(self.detail_url),
        )
        self.assertEqual([response.status_code for response in responses], [403, 403, 403])
        self.assertEqual(Lesson.objects.count(), 2)

    def test_staff_create_persists_and_returns_existing_read_shape(self):
        self.authenticate(self.staff)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, 201, response.data)
        lesson = Lesson.objects.select_related("section", "professor").get(title="Anatomy")
        self.assertEqual(response.data, LessonSerializer(lesson).data)
        self.assertEqual(lesson.section, self.basic)
        self.assertEqual(lesson.professor, self.professor)
        self.assertEqual(lesson.code, "ANAT-101")
        self.assertEqual(response.data["id"], str(lesson.pk))
        self.assertEqual(response.data["views"], 0)
        self.assertIsInstance(response.data["created_at"], str)

    def test_superuser_can_create(self):
        self.authenticate(self.superuser)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, 201, response.data)

    def test_create_without_code_uses_existing_optional_code_contract(self):
        self.authenticate(self.staff)
        payload = {key: value for key, value in self.payload.items() if key != "code"}
        response = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(response.status_code, 201, response.data)
        self.assertNotIn("code", response.data)
        self.assertEqual(Lesson.objects.get(title="Anatomy").code, "")

    def test_create_rejects_invalid_section_professor_title_term_and_code(self):
        self.authenticate(self.staff)
        cases = (
            ("section_slug", "missing"),
            ("professor", "Dr. Missing"),
            ("title", "   "),
            ("term", 0),
            ("term", "not-a-term"),
            ("term", 2**40),
            ("code", None),
        )
        for field, value in cases:
            with self.subTest(field=field, value=value):
                response = self.client.post(
                    self.list_url, {**self.payload, field: value}, format="json"
                )
                self.assertEqual(response.status_code, 400, response.data)
                self.assertIn(field, response.data)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_create_trims_names_and_rejects_ambiguous_professor(self):
        self.authenticate(self.staff)
        response = self.client.post(
            self.list_url,
            {**self.payload, "title": "  Anatomy  ", "professor": "  Dr. Example  "},
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["title"], "Anatomy")
        Professor.objects.create(name="Dr. Example")
        response = self.client.post(
            self.list_url, {**self.payload, "title": "Different Title"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("professor", response.data)

    def test_create_rejects_duplicate_lesson(self):
        self.authenticate(self.staff)
        response = self.client.post(
            self.list_url,
            {
                "section_slug": "basic",
                "title": "Existing Anatomy",
                "professor": "Dr. Example",
                "term": 1,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400, response.data)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_staff_put_updates_all_editable_fields_and_preserves_counters(self):
        self.authenticate(self.staff)
        created_at = self.lesson.created_at
        payload = {
            "section_slug": "clinical",
            "title": "  Updated Anatomy  ",
            "professor": "Dr. Other",
            "term": 4,
            "code": "ANAT-102",
        }
        response = self.client.put(self.detail_url, payload, format="json")
        self.assertEqual(response.status_code, 200, response.data)
        self.lesson.refresh_from_db()
        self.assertEqual(response.data, LessonSerializer(self.lesson).data)
        self.assertEqual(self.lesson.section, self.clinical)
        self.assertEqual(self.lesson.professor, self.other_professor)
        self.assertEqual(self.lesson.title, "Updated Anatomy")
        self.assertEqual(self.lesson.term, 4)
        self.assertEqual(self.lesson.code, "ANAT-102")
        self.assertEqual(self.lesson.views, 7)
        self.assertEqual(self.lesson.created_at, created_at)

    def test_superuser_can_put_and_delete(self):
        self.authenticate(self.superuser)
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, 200, response.data)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 204)

    def test_put_without_code_clears_code_and_requires_other_fields(self):
        self.authenticate(self.staff)
        payload = {key: value for key, value in self.payload.items() if key != "code"}
        response = self.client.put(self.detail_url, payload, format="json")
        self.assertEqual(response.status_code, 200, response.data)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.code, "")
        self.assertNotIn("code", response.data)
        response = self.client.put(self.detail_url, {"title": "Only title"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("section_slug", response.data)
        self.assertIn("professor", response.data)
        self.assertIn("term", response.data)

    def test_put_rejects_invalid_relations_and_term(self):
        self.authenticate(self.staff)
        for field, value in (
            ("section_slug", "missing"),
            ("professor", "Dr. Missing"),
            ("term", -1),
        ):
            with self.subTest(field=field):
                response = self.client.put(
                    self.detail_url, {**self.payload, field: value}, format="json"
                )
                self.assertEqual(response.status_code, 400, response.data)
                self.assertIn(field, response.data)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, "Existing Anatomy")

    def test_unknown_lesson_put_and_delete_return_404(self):
        self.authenticate(self.staff)
        url = reverse("lesson-detail", args=[999999])
        self.assertEqual(self.client.put(url, self.payload, format="json").status_code, 404)
        self.assertEqual(self.client.delete(url).status_code, 404)

    def test_delete_unreferenced_lesson_returns_empty_204(self):
        other_resource = Resource.objects.create(
            lesson=self.other_lesson,
            type=Resource.Type.NOTE,
            title="Other resource",
            status=Resource.Status.APPROVED,
            external_url="https://example.org/other.pdf",
        )
        self.authenticate(self.staff)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertFalse(Lesson.objects.filter(pk=self.lesson.pk).exists())
        self.assertTrue(Resource.objects.filter(pk=other_resource.pk).exists())

    def test_delete_with_resources_returns_400_and_preserves_media(self):
        with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            resource = Resource.objects.create(
                lesson=self.lesson,
                type=Resource.Type.NOTE,
                title="Attached file",
                status=Resource.Status.APPROVED,
                file=SimpleUploadedFile("note.pdf", b"%PDF-1.4\n"),
            )
            file_path = resource.file.path
            self.assertTrue(os.path.exists(file_path))
            self.authenticate(self.staff)
            response = self.client.delete(self.detail_url)
            self.assertEqual(response.status_code, 400, response.data)
            self.assertIn("lesson", response.data)
            self.assertTrue(Lesson.objects.filter(pk=self.lesson.pk).exists())
            self.assertTrue(Resource.objects.filter(pk=resource.pk).exists())
            self.assertTrue(os.path.exists(file_path))

    def test_public_get_list_and_detail_ignore_stale_token(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer stale-token")
        listing = self.client.get(self.list_url)
        detail = self.client.get(self.detail_url)
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data["lesson"], LessonSerializer(self.lesson).data)
