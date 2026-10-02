from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from apps.academics.models import Lesson, Professor, Section


class SeedAcademicsTests(TestCase):
    def test_seed_matches_frontend_mocks_and_is_idempotent(self):
        output = StringIO()
        call_command("seed_academics", stdout=output)

        self.assertEqual(Section.objects.count(), 6)
        self.assertEqual(Professor.objects.count(), 12)
        self.assertEqual(Lesson.objects.count(), 12)
        self.assertEqual(
            list(Section.objects.values_list("slug", "title", "description")),
            [
                ("basic", "علوم پایه", "آناتومی، بیوشیمی، فیزیولوژی و دروس پایه"),
                ("physio", "فیزیوپاتولوژی", "پاتولوژی و فارماکولوژی دستگاه‌ها"),
                ("karamozi", "کارآموزی", "آموزش بالینی مقدماتی و سمیولوژی"),
                ("karvarzi", "کارورزی (اینترنی)", "بخش‌های داخلی، جراحی و کشیک‌ها"),
                ("stage", "استاژری", "استاژرهای تخصصی اطفال، زنان و..."),
                ("general", "دروس عمومی", "زبان، اخلاق پزشکی و دروس عمومی"),
            ],
        )
        self.assertEqual(
            list(Lesson.objects.values_list(
                "section__slug", "title", "professor__name", "term", "code"
            )),
            [
                ("basic", "آناتومی", "دکتر رضایی", 1, "BAS-101"),
                ("basic", "بیوشیمی", "دکتر کریمی", 1, "BAS-102"),
                ("basic", "فیزیولوژی", "دکتر احمدی", 2, "BAS-201"),
                ("physio", "فیزیوپاتولوژی قلب", "دکتر محمدی", 4, "PHY-401"),
                ("physio", "پاتولوژی عمومی", "دکتر حسینی", 4, "PHY-402"),
                ("karamozi", "سمیولوژی", "دکتر نادری", 5, "KAR-501"),
                ("karvarzi", "داخلی ۱", "دکتر صادقی", 7, "KAV-701"),
                ("karvarzi", "جراحی عمومی", "دکتر موسوی", 7, "KAV-702"),
                ("stage", "اطفال", "دکتر فرهادی", 9, "STG-901"),
                ("stage", "زنان و زایمان", "دکتر عزیزی", 9, "STG-902"),
                ("general", "زبان عمومی پزشکی", "دکتر اکبری", 1, "GEN-101"),
                ("general", "اخلاق پزشکی", "دکتر یوسفی", 2, "GEN-201"),
            ],
        )

        section_ids = list(Section.objects.values_list("id", flat=True))
        professor_ids = list(Professor.objects.values_list("id", flat=True))
        lesson_ids = list(Lesson.objects.values_list("id", flat=True))
        Section.objects.filter(slug="basic").update(title="Outdated")
        extra_section = Section.objects.create(slug="elective", title="Elective", order=7)

        call_command("seed_academics", stdout=output)
        self.assertEqual(Section.objects.get(slug="basic").title, "علوم پایه")
        self.assertTrue(Section.objects.filter(pk=extra_section.pk).exists())
        self.assertEqual(
            list(Section.objects.exclude(slug="elective").values_list("id", flat=True)),
            section_ids,
        )
        self.assertEqual(list(Professor.objects.values_list("id", flat=True)), professor_ids)
        self.assertEqual(list(Lesson.objects.values_list("id", flat=True)), lesson_ids)
        self.assertEqual((Section.objects.count(), Professor.objects.count(), Lesson.objects.count()), (7, 12, 12))
        self.assertIn("created 0", output.getvalue())
