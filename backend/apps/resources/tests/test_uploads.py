from io import BytesIO
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from apps.academics.models import Lesson, Professor, Section
from apps.resources.models import Resource


PDF = b"%PDF-1.7\n1 0 obj\n<<>>\nendobj\n"


class UploadWorkflowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        section = Section.objects.create(slug="basic", title="Basic", order=1)
        professor = Professor.objects.create(name="Dr Test")
        cls.lesson = Lesson.objects.create(
            section=section, professor=professor, title="Anatomy", term=1
        )
        users = get_user_model()
        cls.student = users.objects.create_user(student_no="400000001", password="strong-password")
        cls.other = users.objects.create_user(student_no="400000002", password="strong-password")
        cls.staff = users.objects.create_user(
            student_no="400000003", password="strong-password", is_staff=True
        )

    def setUp(self):
        self.media_dir = TemporaryDirectory()
        self.media_override = override_settings(MEDIA_ROOT=self.media_dir.name)
        self.media_override.enable()

    def tearDown(self):
        self.media_override.disable()
        self.media_dir.cleanup()

    def authenticate(self, user=None):
        if user is None:
            self.client.defaults.pop("HTTP_AUTHORIZATION", None)
        else:
            token = RefreshToken.for_user(user).access_token
            self.client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"

    def pdf(self, name="note.pdf", content=PDF, mime="application/pdf"):
        return SimpleUploadedFile(name, content, content_type=mime)

    def upload(self, **overrides):
        data = {
            "lesson": str(self.lesson.pk),
            "professor": "Dr Test",
            "type": Resource.Type.NOTE,
            "title": "Anatomy note",
            "description": "Useful resource",
            "file": self.pdf(),
        }
        data.update(overrides)
        return self.client.post(reverse("resource-upload"), data)

    def resource(self, *, status=Resource.Status.PENDING, owner=None, title="Resource"):
        return Resource.objects.create(
            lesson=self.lesson,
            type=Resource.Type.NOTE,
            title=title,
            file=self.pdf(),
            status=status,
            uploaded_by=owner or self.student,
        )

    def file_response(self, resource):
        response = self.client.get(reverse("resource-file", args=[resource.pk]))
        if response.status_code == 200:
            self.assertEqual(b"".join(response.streaming_content), PDF)
            response.close()
        return response.status_code

    def test_student_upload_is_pending_and_server_controls_ownership_and_review(self):
        self.authenticate(self.student)
        response = self.upload(
            status="approved",
            uploaded_by=str(self.other.pk),
            reviewed_by=str(self.staff.pk),
            reviewed_at="2020-01-01T00:00:00Z",
            section="general",
        )
        self.assertEqual(response.status_code, 201, response.content)
        resource = Resource.objects.get(pk=response.json()["id"])
        self.assertEqual(response.json(), {"id": str(resource.pk), "status": "pending"})
        self.assertEqual(resource.uploaded_by, self.student)
        self.assertIsNone(resource.reviewed_by)
        self.assertIsNone(resource.reviewed_at)
        self.assertEqual(resource.lesson, self.lesson)
        self.assertTrue(resource.file.name.startswith("resources/"))
        self.assertEqual(resource.description, "Useful resource")

    def test_student_cannot_request_direct_upload(self):
        self.authenticate(self.student)
        response = self.upload(direct="true")
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Resource.objects.exists())

    def test_invalid_direct_value_is_rejected(self):
        self.authenticate(self.staff)
        response = self.upload(direct="invalid")
        self.assertEqual(response.status_code, 400)
        self.assertIn("direct", response.json())
        self.assertFalse(Resource.objects.exists())

    def test_anonymous_upload_is_unauthorized(self):
        self.assertEqual(self.upload().status_code, 401)

    def test_upload_rejects_bad_lesson_type_title_professor_and_source(self):
        self.authenticate(self.student)
        cases = (
            ({"lesson": "999999"}, "lesson"),
            ({"type": "invalid"}, "type"),
            ({"title": "  "}, "title"),
            ({"professor": "Another professor"}, "professor"),
            ({"file": ""}, "source"),
            ({"external_url": "https://example.org/note.pdf"}, "source"),
            ({"file": "", "external_url": "ftp://example.org/note.pdf"}, "external_url"),
        )
        for overrides, error_field in cases:
            with self.subTest(overrides=overrides):
                response = self.upload(**overrides)
                self.assertEqual(response.status_code, 400, response.content)
                self.assertIn(error_field, response.json())
        self.assertFalse(Resource.objects.exists())

    def test_external_url_is_valid_as_the_only_source(self):
        self.authenticate(self.student)
        response = self.upload(file="", external_url="https://example.org/note.pdf")
        self.assertEqual(response.status_code, 201, response.content)
        resource = Resource.objects.get(pk=response.json()["id"])
        self.assertFalse(resource.file)
        self.assertEqual(resource.external_url, "https://example.org/note.pdf")

    def test_file_policy_checks_extension_mime_content_and_size(self):
        self.authenticate(self.student)
        cases = (
            self.pdf("malware.exe"),
            self.pdf("note.pdf", mime="application/x-msdownload"),
            self.pdf("note.pdf", content=b"not a PDF"),
            self.pdf("movie.mp4"),
        )
        for file in cases:
            with self.subTest(name=file.name):
                response = self.upload(file=file)
                self.assertEqual(response.status_code, 400, response.content)
                self.assertIn("file", response.json())
        with override_settings(MAX_UPLOAD_SIZE=8):
            response = self.upload()
            self.assertEqual(response.status_code, 400)
            self.assertIn("file", response.json())
        self.assertFalse(Resource.objects.exists())

    def test_video_file_is_accepted(self):
        self.authenticate(self.student)
        video = SimpleUploadedFile(
            "lecture.mp4", b"\x00\x00\x00\x18ftypisom0000", content_type="video/mp4"
        )
        response = self.upload(type=Resource.Type.VIDEO, file=video)
        self.assertEqual(response.status_code, 201, response.content)

    def test_docx_file_and_untrusted_filename_use_resource_storage(self):
        self.authenticate(self.student)
        buffer = BytesIO()
        with ZipFile(buffer, "w") as archive:
            archive.writestr("[Content_Types].xml", "<Types/>")
            archive.writestr("word/document.xml", "<document/>")
        document = SimpleUploadedFile(
            "../../anatomy.docx",
            buffer.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        response = self.upload(file=document)
        self.assertEqual(response.status_code, 201, response.content)
        resource = Resource.objects.get(pk=response.json()["id"])
        self.assertTrue(resource.file.name.startswith("resources/"))
        self.assertNotIn("..", resource.file.name)

    def test_staff_direct_upload_is_reviewed_and_public(self):
        self.authenticate(self.staff)
        response = self.upload(direct="true")
        self.assertEqual(response.status_code, 201, response.content)
        resource = Resource.objects.get(pk=response.json()["id"])
        self.assertEqual(response.json(), {"id": str(resource.pk), "status": "approved"})
        self.assertEqual(resource.uploaded_by, self.staff)
        self.assertEqual(resource.reviewed_by, self.staff)
        self.assertIsNotNone(resource.reviewed_at)
        self.authenticate()
        detail = self.client.get(reverse("lesson-detail", args=[self.lesson.pk])).json()
        self.assertEqual([row["id"] for row in detail["resources"]], [str(resource.pk)])
        self.assertEqual(self.client.get(reverse("site-stats")).json()["notes"], 1)
        self.assertEqual(self.file_response(resource), 200)

    def test_staff_upload_without_direct_is_pending(self):
        self.authenticate(self.staff)
        response = self.upload()
        self.assertEqual(response.status_code, 201)
        resource = Resource.objects.get(pk=response.json()["id"])
        self.assertEqual(response.json()["status"], "pending")
        self.assertIsNone(resource.reviewed_by)
        self.assertIsNone(resource.reviewed_at)
        self.assertEqual(self.client.get(reverse("site-stats")).json()["notes"], 0)
        self.assertEqual(self.client.get(reverse("pending-uploads")).json()[0]["id"], str(resource.pk))

        response = self.upload(direct="false")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["status"], "pending")

    def test_my_uploads_are_private_all_statuses_and_newest_first(self):
        own = [
            self.resource(status=status, title=status)
            for status in (Resource.Status.PENDING, Resource.Status.APPROVED, Resource.Status.REJECTED)
        ]
        self.resource(owner=self.other, title="Other")
        self.assertEqual(self.client.get(reverse("my-uploads")).status_code, 401)
        self.authenticate(self.student)
        response = self.client.get(reverse("my-uploads"))
        self.assertEqual(response.status_code, 200)
        rows = response.json()
        self.assertEqual([row["id"] for row in rows], [str(r.pk) for r in reversed(own)])
        self.assertEqual({row["status"] for row in rows}, set(Resource.Status.values))
        self.assertTrue(all("file_url" in row for row in rows))
        self.authenticate(self.other)
        self.assertEqual(len(self.client.get(reverse("my-uploads")).json()), 1)

    def test_private_file_access_matrix(self):
        resources = {
            status: self.resource(status=status, title=status)
            for status in Resource.Status.values
        }
        for status, resource in resources.items():
            for user, expected in (
                (None, 200 if status == Resource.Status.APPROVED else 404),
                (self.student, 200),
                (self.staff, 200),
                (self.other, 200 if status == Resource.Status.APPROVED else 404),
            ):
                with self.subTest(status=status, user=user):
                    self.authenticate(user)
                    self.assertEqual(self.file_response(resource), expected)
        self.authenticate()
        self.client.defaults["HTTP_AUTHORIZATION"] = "Bearer bad-token"
        self.assertEqual(self.file_response(resources[Resource.Status.APPROVED]), 200)
        self.assertEqual(self.file_response(resources[Resource.Status.PENDING]), 404)

    def test_pending_list_requires_staff_and_only_returns_pending(self):
        pending = self.resource(status=Resource.Status.PENDING)
        newer = self.resource(status=Resource.Status.PENDING, title="Newer")
        self.resource(status=Resource.Status.APPROVED)
        self.resource(status=Resource.Status.REJECTED)
        self.assertEqual(self.client.get(reverse("pending-uploads")).status_code, 401)
        self.authenticate(self.student)
        self.assertEqual(self.client.get(reverse("pending-uploads")).status_code, 403)
        self.authenticate(self.staff)
        response = self.client.get(reverse("pending-uploads"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual([row["id"] for row in response.json()], [str(newer.pk), str(pending.pk)])
        self.assertNotIn("student_no", response.content.decode())

    def test_moderation_permissions_validation_and_transitions(self):
        resource = self.resource()
        url = reverse("moderate-upload", args=[resource.pk])
        self.assertEqual(self.client.post(url, {"action": "approve"}).status_code, 401)
        self.authenticate(self.student)
        self.assertEqual(self.client.post(url, {"action": "approve"}).status_code, 403)
        self.authenticate(self.staff)
        self.assertEqual(self.client.post(url, {"action": "undo"}).status_code, 400)
        missing = reverse("moderate-upload", args=[999999])
        self.assertEqual(self.client.post(missing, {"action": "approve"}).status_code, 404)
        response = self.client.post(
            url, {"action": "approve", "reviewed_by": self.student.pk, "reviewed_at": "2020-01-01"}
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json(), {"id": str(resource.pk), "status": "approved"})
        resource.refresh_from_db()
        self.assertEqual(resource.reviewed_by, self.staff)
        self.assertIsNotNone(resource.reviewed_at)
        self.assertEqual(self.client.post(url, {"action": "reject"}).status_code, 400)
        self.assertEqual(self.client.post(url, {"action": "approve"}).status_code, 400)
        self.authenticate()
        self.assertEqual(
            [row["id"] for row in self.client.get(reverse("lesson-detail", args=[self.lesson.pk])).json()["resources"]],
            [str(resource.pk)],
        )
        self.assertEqual(self.client.get(reverse("site-stats")).json()["notes"], 1)
        self.assertEqual(self.file_response(resource), 200)

        rejected = self.resource(title="Reject me")
        reject_url = reverse("moderate-upload", args=[rejected.pk])
        self.authenticate(self.staff)
        response = self.client.post(reject_url, {"action": "reject"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"id": str(rejected.pk), "status": "rejected"})
        rejected.refresh_from_db()
        self.assertEqual(rejected.reviewed_by, self.staff)
        self.assertIsNotNone(rejected.reviewed_at)
        self.assertEqual(self.client.post(reject_url, {"action": "approve"}).status_code, 400)
        self.assertEqual(self.client.post(reject_url, {"action": "reject"}).status_code, 400)
        self.authenticate()
        self.assertEqual(self.file_response(rejected), 404)
        self.assertEqual(self.client.get(reverse("site-stats")).json()["notes"], 1)
        self.assertEqual(
            len(self.client.get(reverse("lesson-detail", args=[self.lesson.pk])).json()["resources"]),
            1,
        )
