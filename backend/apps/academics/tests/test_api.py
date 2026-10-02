from django.test import TestCase
from django.urls import reverse

from apps.academics.models import Lesson, Professor, Section


class AcademicsAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.general = Section.objects.create(
            slug="general", title="دروس عمومی", description="دروس عمومی", order=2
        )
        cls.basic = Section.objects.create(
            slug="basic", title="علوم پایه", description="دروس پایه", order=1
        )
        cls.professor = Professor.objects.create(name="دکتر رضایی")
        cls.other_professor = Professor.objects.create(name="دکتر کریمی")
        cls.anatomy = Lesson.objects.create(
            section=cls.basic,
            professor=cls.professor,
            title="آناتومی",
            term=1,
            code="BAS-101",
        )
        Lesson.objects.create(
            section=cls.basic, professor=cls.other_professor, title="بیوشیمی", term=1
        )
        Lesson.objects.create(
            section=cls.general,
            professor=cls.professor,
            title="زبان عمومی پزشکی",
            term=2,
            code="GEN-201",
        )

    def test_sections_are_public_ordered_array_with_frontend_fields(self):
        response = self.client.get(
            reverse("section-list"), HTTP_AUTHORIZATION="Bearer stale-token"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual([row["slug"] for row in data], ["basic", "general"])
        self.assertEqual(
            data[0],
            {
                "id": str(self.basic.pk),
                "slug": "basic",
                "title": "علوم پایه",
                "description": "دروس پایه",
            },
        )

    def test_lessons_are_public_array_with_frontend_fields_in_one_query(self):
        with self.assertNumQueries(1):
            response = self.client.get(
                reverse("lesson-list"), HTTP_AUTHORIZATION="Bearer stale-token"
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)
        self.assertEqual(
            data[0],
            {
                "id": str(self.anatomy.pk),
                "section_slug": "basic",
                "title": "آناتومی",
                "professor": "دکتر رضایی",
                "term": 1,
                "code": "BAS-101",
            },
        )
        self.assertIsInstance(data[0]["id"], str)
        self.assertIsInstance(data[0]["term"], int)
        self.assertNotIn("code", data[1])
        for row in data:
            self.assertNotIn("section_id", row)
            self.assertNotIn("professor_id", row)

    def test_lesson_detail_has_empty_resources_and_unknown_id_is_404(self):
        response = self.client.get(reverse("lesson-detail", args=[self.anatomy.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "lesson": {
                    "id": str(self.anatomy.pk),
                    "section_slug": "basic",
                    "title": "آناتومی",
                    "professor": "دکتر رضایی",
                    "term": 1,
                    "code": "BAS-101",
                },
                "resources": [],
            },
        )
        self.assertEqual(
            self.client.get(reverse("lesson-detail", args=[999999])).status_code, 404
        )

    def test_unimplemented_filters_are_rejected_and_writes_are_not_public(self):
        response = self.client.get(reverse("lesson-list"), {"section": "basic"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.client.post(reverse("lesson-list"), {}).status_code, 405)
