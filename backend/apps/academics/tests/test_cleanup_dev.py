from io import StringIO
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from apps.academics.models import Lesson, Professor, Section
from apps.resources.models import Resource


class CleanupDevTestDataTests(TestCase):
    def setUp(self):
        self.section = Section.objects.create(slug="basic", title="Basic", order=1)
        self.professor = Professor.objects.create(name="Professor")
        self.lesson = Lesson.objects.create(
            section=self.section, professor=self.professor, title="Anatomy", term=1
        )
        user_model = get_user_model()
        self.test_user = user_model.objects.create_user(
            student_no="499005678", password="StrongPass!2026"
        )
        self.other_test_user = user_model.objects.create_user(
            student_no="499001234", password="StrongPass!2026"
        )
        self.normal_user = user_model.objects.create_user(
            student_no="402130433", password="StrongPass!2026"
        )

    @override_settings(DEBUG=True)
    def test_cleanup_deletes_only_named_artifacts_and_their_unshared_files(self):
        with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            artifact = Resource.objects.create(
                lesson=self.lesson,
                type=Resource.Type.NOTE,
                title="E2E-TEST-UPLOAD",
                file=SimpleUploadedFile("artifact.pdf", b"%PDF-1.4\n"),
                uploaded_by=self.test_user,
            )
            unrelated = Resource.objects.create(
                lesson=self.lesson,
                type=Resource.Type.NOTE,
                title="Real resource",
                file=SimpleUploadedFile("real.pdf", b"%PDF-1.4\n"),
                uploaded_by=self.test_user,
            )
            artifact_path = artifact.file.path
            unrelated_path = unrelated.file.path
            unused_professor = Professor.objects.create(name="Test Prof")

            output = StringIO()
            with self.captureOnCommitCallbacks(execute=True):
                call_command("cleanup_dev_test_data", "--yes", stdout=output)

            self.assertIn("499005678", output.getvalue())
            self.assertIn("1 uploads, 0 reviews", output.getvalue())
            self.assertFalse(get_user_model().objects.filter(student_no__startswith="499").exists())
            self.assertTrue(get_user_model().objects.filter(pk=self.normal_user.pk).exists())
            self.assertFalse(Resource.objects.filter(pk=artifact.pk).exists())
            self.assertTrue(Resource.objects.filter(pk=unrelated.pk).exists())
            self.assertIsNone(Resource.objects.get(pk=unrelated.pk).uploaded_by_id)
            self.assertFalse(Professor.objects.filter(pk=unused_professor.pk).exists())
            self.assertFalse(artifact.file.storage.exists(artifact.file.name))
            self.assertTrue(unrelated.file.storage.exists(unrelated.file.name))
            self.assertNotEqual(artifact_path, unrelated_path)

    @override_settings(DEBUG=True)
    def test_cleanup_requires_confirmation_and_keeps_referenced_test_professor(self):
        used_professor = Professor.objects.create(name="Test Prof")
        self.lesson.professor = used_professor
        self.lesson.save(update_fields=["professor"])
        output = StringIO()

        with self.assertRaisesMessage(CommandError, "pass --yes"):
            call_command("cleanup_dev_test_data", stdout=output)
        self.assertIn("499005678", output.getvalue())
        self.assertTrue(get_user_model().objects.filter(pk=self.test_user.pk).exists())

        call_command("cleanup_dev_test_data", "--yes", stdout=StringIO())
        self.assertTrue(Professor.objects.filter(pk=used_professor.pk).exists())
        self.assertEqual(Lesson.objects.get(pk=self.lesson.pk).professor, used_professor)

    @override_settings(DEBUG=False)
    def test_cleanup_refuses_non_debug_environment(self):
        with self.assertRaisesMessage(CommandError, "disabled unless DEBUG=True"):
            call_command("cleanup_dev_test_data", "--yes", stdout=StringIO())
        self.assertTrue(get_user_model().objects.filter(pk=self.test_user.pk).exists())

    @override_settings(DEBUG=True)
    def test_seed_repairs_histology_before_cleanup_removes_test_professor(self):
        test_professor = Professor.objects.create(name="Test Prof")
        Lesson.objects.create(
            section=self.section,
            professor=test_professor,
            title="بافت‌شناسی",
            term=9,
        )

        call_command("seed_academics", stdout=StringIO())
        call_command("cleanup_dev_test_data", "--yes", stdout=StringIO())

        histology = Lesson.objects.get(section=self.section, title="بافت‌شناسی")
        self.assertEqual(histology.professor.name, "دکتر شریفی")
        self.assertFalse(Professor.objects.filter(pk=test_professor.pk).exists())
