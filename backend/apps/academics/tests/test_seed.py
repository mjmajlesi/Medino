from io import StringIO
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from apps.academics.management.commands.seed_academics import LESSONS, SECTIONS
from apps.academics.models import Lesson, Professor, Section
from apps.resources.models import Resource


class SeedAcademicsTests(TestCase):
    def test_seed_creates_approved_catalog_and_is_idempotent(self):
        output = StringIO()
        call_command("seed_academics", stdout=output)

        self.assertEqual(len(LESSONS), 75)
        self.assertEqual(len({(slug, title) for slug, title, *_ in LESSONS}), 75)
        self.assertEqual((Section.objects.count(), Professor.objects.count(), Lesson.objects.count()), (6, 26, 75))
        self.assertEqual(
            list(Section.objects.values_list("slug", "title", "description")),
            [(slug, title, description) for slug, title, description in SECTIONS],
        )
        self.assertEqual(
            set(Lesson.objects.values_list(
                "section__slug", "title", "professor__name", "term", "code"
            )),
            set(LESSONS),
        )
        self.assertEqual(
            set(Professor.objects.values_list("name", flat=True)),
            {professor for _, _, professor, _, _ in LESSONS},
        )
        self.assertFalse(Lesson.objects.filter(
            title__in=("زبان عمومی پزشکی", "اخلاق پزشکی")
        ).exists())
        self.assertEqual(
            Lesson.objects.get(section__slug="basic", title="بافت‌شناسی").professor.name,
            "دکتر شریفی",
        )
        embryology = Lesson.objects.get(section__slug="basic", title="جنین‌شناسی")
        self.assertEqual(
            (embryology.professor.name, embryology.term, embryology.code),
            ("دکتر قاسمی", 1, "BAS-103"),
        )

        section_ids = dict(Section.objects.values_list("slug", "id"))
        professor_ids = dict(Professor.objects.values_list("name", "id"))
        lesson_ids = dict(Lesson.objects.values_list("title", "id").filter(section__slug="basic"))
        Section.objects.filter(slug="basic").update(title="Outdated")
        extra_section = Section.objects.create(slug="elective", title="Elective", order=7)

        call_command("seed_academics", stdout=output)
        self.assertEqual(Section.objects.get(slug="basic").title, "علوم پایه")
        self.assertTrue(Section.objects.filter(pk=extra_section.pk).exists())
        self.assertEqual(dict(Section.objects.exclude(slug="elective").values_list("slug", "id")), section_ids)
        self.assertEqual(dict(Professor.objects.values_list("name", "id")), professor_ids)
        self.assertEqual(
            dict(Lesson.objects.filter(section__slug="basic").values_list("title", "id")),
            lesson_ids,
        )
        self.assertEqual((Section.objects.count(), Professor.objects.count(), Lesson.objects.count()), (7, 26, 75))
        self.assertIn("Lessons: 75 (created 0, updated 0, deleted 0)", output.getvalue())

    def make_legacy_database(self):
        sections = {
            slug: Section.objects.create(
                slug=slug, title=title, description=description, order=order
            )
            for order, (slug, title, description) in enumerate(SECTIONS, start=1)
        }
        required_names = sorted({professor for _, _, professor, _, _ in LESSONS})
        self.assertEqual(len(required_names), 26)
        existing_names = required_names[:10] + [
            "Legacy Professor One", "Legacy Professor Two", "Test Prof"
        ]
        professors = {
            name: Professor.objects.create(name=name) for name in existing_names
        }
        for slug, title, _, _, _ in LESSONS[:3]:
            Lesson.objects.create(
                section=sections[slug], title=title,
                professor=professors[required_names[9]], term=9, code="OLD",
            )
        stale = []
        for index in range(9):
            stale.append(Lesson.objects.create(
                section=sections["basic"], title=f"Legacy Lesson {index + 1}",
                professor=professors[existing_names[10 + index % 3]], term=1,
            ))
        return stale

    def test_legacy_database_default_keeps_stale_rows_and_prune_reconciles(self):
        stale = self.make_legacy_database()
        user = get_user_model().objects.create_user(
            student_no="402130433", password="StrongPass!2026"
        )

        normal_output = StringIO()
        call_command("seed_academics", stdout=normal_output)
        self.assertEqual((Section.objects.count(), Professor.objects.count(), Lesson.objects.count()), (6, 29, 84))
        self.assertIn("created 72, updated 3, deleted 0", normal_output.getvalue())
        self.assertEqual(Lesson.objects.filter(pk__in=[lesson.pk for lesson in stale]).count(), 9)

        approved = Lesson.objects.get(section__slug="basic", title="آناتومی")
        resource = Resource.objects.create(
            lesson=approved,
            type=Resource.Type.VIDEO,
            title="Student resource",
            external_url="https://example.org/lesson-video",
            uploaded_by=user,
        )
        prune_output = StringIO()
        call_command("seed_academics", "--prune", stdout=prune_output)
        self.assertEqual((Section.objects.count(), Professor.objects.count(), Lesson.objects.count()), (6, 26, 75))
        self.assertFalse(Lesson.objects.filter(pk__in=[lesson.pk for lesson in stale]).exists())
        self.assertTrue(get_user_model().objects.filter(pk=user.pk).exists())
        self.assertTrue(Resource.objects.filter(pk=resource.pk, uploaded_by=user).exists())
        self.assertEqual(
            set(Lesson.objects.values_list("section__slug", "title", "professor__name", "term", "code")),
            set(LESSONS),
        )
        self.assertIn("created 0, updated 0, deleted 9", prune_output.getvalue())

        lesson_ids = set(Lesson.objects.values_list("pk", flat=True))
        second_output = StringIO()
        call_command("seed_academics", "--prune", stdout=second_output)
        self.assertEqual(set(Lesson.objects.values_list("pk", flat=True)), lesson_ids)
        self.assertEqual((Section.objects.count(), Professor.objects.count(), Lesson.objects.count()), (6, 26, 75))
        self.assertIn("created 0, updated 0, deleted 0", second_output.getvalue())

    def test_prune_dry_run_reports_changes_without_writing(self):
        self.make_legacy_database()
        output = StringIO()

        with CaptureQueriesContext(connection) as queries:
            call_command("seed_academics", "--prune", "--dry-run", stdout=output)

        self.assertFalse(any(
            query["sql"].lstrip().upper().startswith(("INSERT", "UPDATE", "DELETE"))
            for query in queries
        ))
        self.assertEqual((Section.objects.count(), Professor.objects.count(), Lesson.objects.count()), (6, 13, 12))
        report = output.getvalue()
        self.assertIn("Lessons to create (72)", report)
        self.assertIn("Lessons to update (3)", report)
        self.assertIn("Stale lessons safe to delete (9)", report)
        self.assertIn("Stale lessons blocked by resources (0)", report)
        self.assertIn("Professors safe to delete (3)", report)
        self.assertIn("Expected final counts: Sections 6; Professors 26; Lessons 75", report)

    def test_prune_keeps_stale_lesson_with_resource_and_file(self):
        call_command("seed_academics", stdout=StringIO())
        user = get_user_model().objects.create_user(
            student_no="402130433", password="StrongPass!2026"
        )
        blocked_professor = Professor.objects.create(name="Professor With Upload")
        blocked = Lesson.objects.create(
            section=Section.objects.get(slug="basic"), title="Legacy With Upload",
            professor=blocked_professor, term=1,
        )
        safe_professor = Professor.objects.create(name="Unused Legacy Professor")
        safe = Lesson.objects.create(
            section=blocked.section, title="Legacy Without Upload",
            professor=safe_professor, term=1,
        )
        with TemporaryDirectory() as media_root, self.settings(MEDIA_ROOT=media_root):
            resource = Resource.objects.create(
                lesson=blocked, type=Resource.Type.NOTE, title="User upload",
                file=SimpleUploadedFile("keep.pdf", b"%PDF-1.4\n"), uploaded_by=user,
            )
            output = StringIO()
            call_command("seed_academics", "--prune", "--dry-run", stdout=output)
            self.assertIn("Stale lessons blocked by resources (1)", output.getvalue())
            self.assertIn(f"id {blocked.pk}: basic/Legacy With Upload; resources 1", output.getvalue())

            with self.captureOnCommitCallbacks(execute=True):
                call_command("seed_academics", "--prune", stdout=output)

            self.assertFalse(Lesson.objects.filter(pk=safe.pk).exists())
            self.assertFalse(Professor.objects.filter(pk=safe_professor.pk).exists())
            self.assertTrue(Lesson.objects.filter(pk=blocked.pk).exists())
            self.assertTrue(Professor.objects.filter(pk=blocked_professor.pk).exists())
            self.assertTrue(Resource.objects.filter(pk=resource.pk, uploaded_by=user).exists())
            self.assertTrue(resource.file.storage.exists(resource.file.name))
            self.assertTrue(get_user_model().objects.filter(pk=user.pk).exists())
            self.assertIn("PRUNE INCOMPLETE: 1 stale lessons have resources", output.getvalue())
            self.assertEqual((Section.objects.count(), Professor.objects.count(), Lesson.objects.count()), (6, 27, 76))

    def test_seed_reuses_section_title_identity_when_assignment_changes(self):
        section = Section.objects.create(slug="basic", title="Basic", order=1)
        wrong_professor = Professor.objects.create(name="Test Prof")
        lesson = Lesson.objects.create(
            section=section,
            title="بافت‌شناسی",
            professor=wrong_professor,
            term=9,
            code="WRONG",
        )

        call_command("seed_academics", stdout=StringIO())

        lesson.refresh_from_db()
        self.assertEqual(lesson.pk, Lesson.objects.get(section=section, title="بافت‌شناسی").pk)
        self.assertEqual((lesson.professor.name, lesson.term, lesson.code), ("دکتر شریفی", 1, ""))
        self.assertEqual(Lesson.objects.filter(section=section, title="بافت‌شناسی").count(), 1)

    def test_seed_rejects_ambiguous_existing_lesson_without_partial_writes(self):
        section = Section.objects.create(slug="basic", title="Basic", order=1)
        first = Professor.objects.create(name="First")
        second = Professor.objects.create(name="Second")
        Lesson.objects.create(section=section, title="بافت‌شناسی", professor=first, term=1)
        Lesson.objects.create(section=section, title="بافت‌شناسی", professor=second, term=1)

        with self.assertRaisesMessage(CommandError, "Lesson identity is ambiguous"):
            call_command("seed_academics", stdout=StringIO())

        self.assertEqual(Section.objects.count(), 1)
        self.assertEqual(Professor.objects.count(), 2)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_seed_rejects_ambiguous_professor_without_partial_writes(self):
        Professor.objects.create(name="دکتر رضایی")
        Professor.objects.create(name="دکتر رضایی")

        with self.assertRaisesMessage(CommandError, "Professor name is ambiguous"):
            call_command("seed_academics", stdout=StringIO())

        self.assertEqual(Section.objects.count(), 0)
        self.assertEqual(Professor.objects.count(), 2)
        self.assertEqual(Lesson.objects.count(), 0)
