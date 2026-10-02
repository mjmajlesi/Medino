from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.academics.models import Lesson, Professor, Section


class AcademicsModelTests(TestCase):
    def test_section_creation_ordering_and_unique_slug(self):
        Section.objects.create(slug="general", title="دروس عمومی", order=2)
        Section.objects.create(slug="basic", title="علوم پایه", order=1)
        self.assertEqual(
            list(Section.objects.values_list("slug", flat=True)),
            ["basic", "general"],
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            Section.objects.create(slug="basic", title="Duplicate", order=3)

    def test_professor_and_lesson_relationships_and_optional_code(self):
        section = Section.objects.create(slug="basic", title="علوم پایه", order=1)
        professor = Professor.objects.create(name="دکتر رضایی")
        lesson = Lesson.objects.create(
            section=section, professor=professor, title="آناتومی", term=1
        )

        self.assertEqual(professor.name, "دکتر رضایی")
        self.assertEqual(lesson.section, section)
        self.assertEqual(lesson.professor, professor)
        self.assertEqual(lesson.term, 1)
        self.assertEqual(lesson.code, "")
        self.assertEqual(list(section.lessons.all()), [lesson])
        self.assertEqual(list(professor.lessons.all()), [lesson])

        with self.assertRaises(IntegrityError), transaction.atomic():
            Lesson.objects.create(
                section=section, professor=professor, title="آناتومی", term=1
            )
