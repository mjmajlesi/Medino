from django.test import TestCase
from django.urls import reverse

from apps.academics.models import Lesson, Professor, Section
from apps.resources.models import Resource


class SiteStatsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        section = Section.objects.create(slug="basic", title="علوم پایه", order=1)
        professor = Professor.objects.create(name="دکتر رضایی")
        cls.lesson = Lesson.objects.create(
            section=section, professor=professor, title="آناتومی", term=1
        )
        Lesson.objects.create(
            section=section, professor=professor, title="بیوشیمی", term=1
        )

    def test_stats_count_all_lessons_and_only_approved_resources_by_type(self):
        for resource_type in Resource.Type.values:
            Resource.objects.create(
                lesson=self.lesson,
                type=resource_type,
                title=f"Approved {resource_type}",
                status=Resource.Status.APPROVED,
                external_url=f"https://example.org/{resource_type}",
            )
        for status in (Resource.Status.PENDING, Resource.Status.REJECTED):
            Resource.objects.create(
                lesson=self.lesson,
                type=Resource.Type.NOTE,
                title=f"Unpublished {status}",
                status=status,
                external_url=f"https://example.org/{status}",
            )

        with self.assertNumQueries(2):
            response = self.client.get(
                reverse("site-stats"), HTTP_AUTHORIZATION="Bearer stale-token"
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "lessons": 2,
            "notes": 1,
            "videos": 1,
            "samples": 1,
            "summaries": 1,
        })
