from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from apps.academics.management.commands.seed_academics import LESSONS, SECTIONS
from apps.academics.models import Lesson, Professor, Section


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
        self.assertIn("Lessons: 75 (created 0, updated 75)", output.getvalue())

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
