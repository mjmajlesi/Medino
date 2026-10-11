import os
from tempfile import TemporaryDirectory

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from apps.academics.models import Lesson, Professor, Section
from apps.resources.models import Resource


class ResourceFileCleanupTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        section = Section.objects.create(slug="basic", title="Basic", order=1)
        professor = Professor.objects.create(name="Dr. Example")
        cls.lesson = Lesson.objects.create(
            section=section, professor=professor, title="Anatomy", term=1
        )

    def test_direct_resource_delete_removes_uploaded_file(self):
        with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            resource = Resource.objects.create(
                lesson=self.lesson,
                type=Resource.Type.NOTE,
                title="Direct deletion",
                file=SimpleUploadedFile("direct.pdf", b"%PDF-1.4\n"),
            )
            file_path = resource.file.path
            self.assertTrue(os.path.exists(file_path))
            with self.captureOnCommitCallbacks(execute=True):
                resource.delete()
            self.assertFalse(Resource.objects.filter(pk=resource.pk).exists())
            self.assertFalse(os.path.exists(file_path))

    def test_shared_file_is_retained_until_last_reference_is_deleted(self):
        with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            first = Resource.objects.create(
                lesson=self.lesson,
                type=Resource.Type.NOTE,
                title="First reference",
                file=SimpleUploadedFile("shared.pdf", b"%PDF-1.4\n"),
            )
            second = Resource.objects.create(
                lesson=self.lesson,
                type=Resource.Type.NOTE,
                title="Second reference",
                file=first.file.name,
            )
            file_path = first.file.path
            with self.captureOnCommitCallbacks(execute=True):
                first.delete()
            self.assertTrue(os.path.exists(file_path))
            self.assertTrue(Resource.objects.filter(pk=second.pk).exists())
            with self.captureOnCommitCallbacks(execute=True):
                second.delete()
            self.assertFalse(os.path.exists(file_path))
