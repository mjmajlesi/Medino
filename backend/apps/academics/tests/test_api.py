from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.academics.models import Lesson, Professor, Section
from apps.resources.models import Resource


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
        cls.biochemistry = Lesson.objects.create(
            section=cls.basic, professor=cls.other_professor, title="بیوشیمی", term=1
        )
        cls.language = Lesson.objects.create(
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
            {key: value for key, value in data[0].items() if key != "created_at"},
            {
                "id": str(self.anatomy.pk),
                "section_slug": "basic",
                "title": "آناتومی",
                "professor": "دکتر رضایی",
                "term": 1,
                "code": "BAS-101",
                "views": 0,
            },
        )
        self.assertIsInstance(data[0]["created_at"], str)
        self.assertIsInstance(data[0]["id"], str)
        self.assertIsInstance(data[0]["term"], int)
        self.assertNotIn("code", data[1])
        for row in data:
            self.assertNotIn("section_id", row)
            self.assertNotIn("professor_id", row)

    def test_lesson_detail_has_empty_resources_and_unknown_id_is_404(self):
        response = self.client.get(reverse("lesson-detail", args=[self.anatomy.pk]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data["lesson"].pop("created_at"), str)
        self.assertEqual(
            data,
            {
                "lesson": {
                    "id": str(self.anatomy.pk),
                    "section_slug": "basic",
                    "title": "آناتومی",
                    "professor": "دکتر رضایی",
                    "term": 1,
                    "code": "BAS-101",
                    "views": 0,
                },
                "resources": [],
            },
        )
        self.assertEqual(
            self.client.get(reverse("lesson-detail", args=[999999])).status_code, 404
        )

    def test_filters_are_available_and_writes_are_not_public(self):
        response = self.client.get(reverse("lesson-list"), {"section": "basic"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(self.client.post(reverse("lesson-list"), {}).status_code, 405)

    def lesson_ids(self, **filters):
        response = self.client.get(reverse("lesson-list"), filters)
        self.assertEqual(response.status_code, 200, response.content)
        self.assertIsInstance(response.json(), list)
        return [row["id"] for row in response.json()]

    def add_resource(self, lesson, status, resource_type=Resource.Type.NOTE):
        return Resource.objects.create(
            lesson=lesson,
            title="Test resource",
            type=resource_type,
            status=status,
            external_url="https://example.org/resource.pdf",
        )

    def test_section_filter_and_no_match(self):
        self.assertEqual(
            self.lesson_ids(section="basic"),
            [str(self.anatomy.pk), str(self.biochemistry.pk)],
        )
        self.assertEqual(self.lesson_ids(section="unknown"), [])

    def test_search_matches_lesson_title_and_professor_name(self):
        self.assertEqual(self.lesson_ids(search="  آناتومی  "), [str(self.anatomy.pk)])
        self.assertEqual(
            self.lesson_ids(search="رضایی"),
            [str(self.anatomy.pk), str(self.language.pk)],
        )
        self.assertEqual(self.lesson_ids(search="not-found"), [])
        english = Lesson.objects.create(
            section=self.basic, professor=self.other_professor, title="Cardiology", term=3
        )
        self.assertEqual(self.lesson_ids(search="CARDIO"), [str(english.pk)])

    def test_professor_is_partial_and_term_is_exact(self):
        self.assertEqual(self.lesson_ids(professor="کری"), [str(self.biochemistry.pk)])
        self.assertEqual(
            self.lesson_ids(term="1"),
            [str(self.anatomy.pk), str(self.biochemistry.pk)],
        )
        self.assertEqual(self.lesson_ids(term="99"), [])

    def test_type_requires_approved_resource_and_deduplicates_lessons(self):
        self.add_resource(self.anatomy, Resource.Status.APPROVED)
        self.add_resource(self.anatomy, Resource.Status.APPROVED)
        self.add_resource(self.biochemistry, Resource.Status.PENDING)
        self.add_resource(self.language, Resource.Status.REJECTED)
        with self.assertNumQueries(1):
            ids = self.lesson_ids(type="note")
        self.assertEqual(ids, [str(self.anatomy.pk)])
        self.assertEqual(self.lesson_ids(type="video"), [])

    def test_filters_compose_on_one_queryset(self):
        self.add_resource(self.anatomy, Resource.Status.APPROVED)
        self.add_resource(self.biochemistry, Resource.Status.APPROVED)
        self.add_resource(self.language, Resource.Status.APPROVED)
        self.add_resource(self.language, Resource.Status.APPROVED, Resource.Type.VIDEO)
        self.assertEqual(
            self.lesson_ids(section="basic", term="1", search="آناتومی", type="note"),
            [str(self.anatomy.pk)],
        )
        self.assertEqual(
            self.lesson_ids(section="basic", professor="رضایی", type="video"), []
        )
        self.assertEqual(
            self.lesson_ids(section="general", professor="رضایی", type="video"),
            [str(self.language.pk)],
        )

    def test_invalid_term_and_type_return_field_errors(self):
        for filters, field in (
            ({"term": "abc"}, "term"),
            ({"term": "0"}, "term"),
            ({"term": "-1"}, "term"),
            ({"term": "1.5"}, "term"),
            ({"type": "invalid"}, "type"),
        ):
            with self.subTest(filters=filters):
                response = self.client.get(reverse("lesson-list"), filters)
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.json())

    def test_unknown_parameters_are_ignored_like_existing_endpoint(self):
        self.assertEqual(
            self.lesson_ids(foo="bar"),
            [str(self.anatomy.pk), str(self.biochemistry.pk), str(self.language.pk)],
        )

    def test_frontend_sorting_uses_stored_values(self):
        now = timezone.now()
        Lesson.objects.filter(pk=self.anatomy.pk).update(created_at=now - timedelta(days=2))
        Lesson.objects.filter(pk=self.biochemistry.pk).update(created_at=now)
        Lesson.objects.filter(pk=self.language.pk).update(created_at=now - timedelta(days=1))
        self.assertEqual(
            self.lesson_ids(ordering="-created_at"),
            [str(self.biochemistry.pk), str(self.language.pk), str(self.anatomy.pk)],
        )

        Lesson.objects.filter(pk=self.language.pk).update(views=7)
        Lesson.objects.filter(pk=self.anatomy.pk).update(views=3)
        self.assertEqual(
            self.lesson_ids(ordering="-views"),
            [str(self.language.pk), str(self.anatomy.pk), str(self.biochemistry.pk)],
        )
        self.assertEqual(self.client.get(reverse("lesson-list"), {"ordering": "invalid"}).status_code, 400)

    def test_lesson_detail_does_not_change_stored_views(self):
        Lesson.objects.filter(pk=self.anatomy.pk).update(views=7)
        detail_url = reverse("lesson-detail", args=[self.anatomy.pk])
        for _ in range(3):
            response = self.client.get(detail_url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["lesson"]["views"], 7)
            self.assertEqual(Lesson.objects.get(pk=self.anatomy.pk).views, 7)
