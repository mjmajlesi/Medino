"""Seed local academic data from the frontend Section and Lesson mocks."""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.academics.models import Lesson, Professor, Section


SECTIONS = (
    ("basic", "علوم پایه", "آناتومی، بیوشیمی، فیزیولوژی و دروس پایه"),
    ("physio", "فیزیوپاتولوژی", "پاتولوژی و فارماکولوژی دستگاه‌ها"),
    ("karamozi", "کارآموزی", "آموزش بالینی مقدماتی و سمیولوژی"),
    ("karvarzi", "کارورزی (اینترنی)", "بخش‌های داخلی، جراحی و کشیک‌ها"),
    ("stage", "استاژری", "استاژرهای تخصصی اطفال، زنان و..."),
    ("general", "دروس عمومی", "زبان، اخلاق پزشکی و دروس عمومی"),
)

LESSONS = (
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
)


class Command(BaseCommand):
    help = "Create or update local Section, Professor, and Lesson mock data."

    @transaction.atomic
    def handle(self, *args, **options):
        section_counts = {"created": 0, "updated": 0}
        professor_created = 0
        lesson_counts = {"created": 0, "updated": 0}

        sections = {}
        for order, (slug, title, description) in enumerate(SECTIONS, start=1):
            section, created = Section.objects.update_or_create(
                slug=slug,
                defaults={"title": title, "description": description, "order": order},
            )
            sections[slug] = section
            section_counts["created" if created else "updated"] += 1

        professors = {}
        for section_slug, title, professor_name, term, code in LESSONS:
            professor = professors.get(professor_name)
            if professor is None:
                professor = Professor.objects.filter(name=professor_name).order_by("id").first()
                if professor is None:
                    professor = Professor.objects.create(name=professor_name)
                    professor_created += 1
                professors[professor_name] = professor

            _, created = Lesson.objects.update_or_create(
                section=sections[section_slug],
                title=title,
                professor=professor,
                term=term,
                defaults={"code": code},
            )
            lesson_counts["created" if created else "updated"] += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Sections: {len(SECTIONS)} (created {section_counts['created']}, "
                f"updated {section_counts['updated']}); "
                f"Professors: {len(professors)} (created {professor_created}); "
                f"Lessons: {len(LESSONS)} (created {lesson_counts['created']}, "
                f"updated {lesson_counts['updated']})."
            )
        )
