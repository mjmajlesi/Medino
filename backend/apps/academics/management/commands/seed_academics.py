"""Seed the approved academic catalog represented by docs/lessons-seed.json."""

from django.core.management.base import BaseCommand, CommandError
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

# (section slug, title) is the stable identity. IDs and professor assignments
# can change without creating another Lesson.
LESSONS = (
    ("basic", "آناتومی", "دکتر رضایی", 1, "BAS-101"),
    ("basic", "بیوشیمی", "دکتر کریمی", 1, "BAS-102"),
    ("basic", "فیزیولوژی", "دکتر احمدی", 2, "BAS-201"),
    ("basic", "آسیب‌شناسی عمومی", "دکتر حسینی", 4, "PHY-402"),
    ("basic", "بافت‌شناسی", "دکتر شریفی", 1, ""),
    ("basic", "جنین‌شناسی", "دکتر قاسمی", 1, "BAS-103"),
    ("basic", "زیست‌شناسی سلولی و مولکولی", "دکتر نجفی", 8, ""),
    ("basic", "ژنتیک پزشکی", "دکتر حیدری", 8, ""),
    ("basic", "فیزیک پزشکی", "دکتر امینی", 9, ""),
    ("basic", "بیوفیزیک", "دکتر شریفی", 4, ""),
    ("basic", "میکروب‌شناسی", "دکتر کاظمی", 3, ""),
    ("basic", "باکتری‌شناسی", "دکتر امینی", 9, ""),
    ("basic", "ویروس‌شناسی", "دکتر شریفی", 8, ""),
    ("basic", "انگل‌شناسی", "دکتر فرهمند", 3, ""),
    ("basic", "قارچ‌شناسی", "دکتر حیدری", 2, ""),
    ("basic", "ایمنی‌شناسی", "دکتر حیدری", 8, ""),
    ("basic", "آسیب‌شناسی اختصاصی", "دکتر سعیدی", 5, ""),
    ("basic", "فارماکولوژی", "دکتر شهیدی", 3, ""),
    ("basic", "اپیدمیولوژی", "دکتر سعیدی", 2, ""),
    ("basic", "آمار زیستی", "دکتر قاسمی", 9, ""),
    ("basic", "بهداشت عمومی", "دکتر شهیدی", 1, ""),
    ("basic", "تغذیه", "دکتر نجفی", 7, ""),
    ("basic", "زبان تخصصی پزشکی", "دکتر باقری", 8, ""),
    ("basic", "اصطلاحات پزشکی", "دکتر کاظمی", 3, ""),
    ("physio", "فیزیوپاتولوژی قلب و عروق", "دکتر محمدی", 4, "PHY-401"),
    ("physio", "سمیولوژی", "دکتر نادری", 5, "KAR-501"),
    ("physio", "فیزیوپاتولوژی تنفس", "دکتر حیدری", 1, ""),
    ("physio", "فیزیوپاتولوژی کلیه", "دکتر شریفی", 9, ""),
    ("physio", "فیزیوپاتولوژی گوارش", "دکتر توکلی", 2, ""),
    ("physio", "فیزیوپاتولوژی غدد درون‌ریز", "دکتر جعفری", 1, ""),
    ("physio", "فیزیوپاتولوژی خون", "دکتر مرادی", 1, ""),
    ("physio", "فیزیوپاتولوژی روماتولوژی", "دکتر سعیدی", 4, ""),
    ("physio", "فیزیوپاتولوژی اعصاب", "دکتر نجفی", 4, ""),
    ("physio", "فیزیوپاتولوژی روان", "دکتر شریفی", 1, ""),
    ("physio", "فارماکولوژی", "دکتر فرهمند", 8, ""),
    ("physio", "آسیب‌شناسی بالینی", "دکتر شریفی", 6, ""),
    ("physio", "مهارت‌های بالینی", "دکتر سعیدی", 8, ""),
    ("karamozi", "کودکان", "دکتر فرهادی", 9, "STG-901"),
    ("karamozi", "زنان و زایمان", "دکتر عزیزی", 9, "STG-902"),
    ("karamozi", "داخلی", "دکتر توکلی", 4, ""),
    ("karamozi", "جراحی عمومی", "دکتر باقری", 9, ""),
    ("karamozi", "قلب و عروق", "دکتر رستمی", 4, ""),
    ("karamozi", "بیماری‌های عفونی", "دکتر قاسمی", 5, ""),
    ("karamozi", "مغز و اعصاب", "دکتر مرادی", 8, ""),
    ("karamozi", "ارتوپدی", "دکتر قاسمی", 1, ""),
    ("karamozi", "اورولوژی", "دکتر قاسمی", 2, ""),
    ("karamozi", "چشم‌پزشکی", "دکتر حیدری", 8, ""),
    ("karamozi", "گوش، حلق و بینی", "دکتر مرادی", 5, ""),
    ("karamozi", "پوست", "دکتر عسگری", 7, ""),
    ("karamozi", "روان‌پزشکی", "دکتر شهیدی", 9, ""),
    ("karamozi", "رادیولوژی", "دکتر شهیدی", 2, ""),
    ("karamozi", "بیهوشی", "دکتر امینی", 5, ""),
    ("karamozi", "پزشکی قانونی", "دکتر قاسمی", 6, ""),
    ("karamozi", "بهداشت", "دکتر قاسمی", 4, ""),
    ("karamozi", "پزشکی اورژانس", "دکتر جعفری", 9, ""),
    ("karvarzi", "داخلی", "دکتر صادقی", 7, "KAV-701"),
    ("karvarzi", "جراحی عمومی", "دکتر موسوی", 7, "KAV-702"),
    ("karvarzi", "کودکان", "دکتر فرهمند", 5, ""),
    ("karvarzi", "زنان و زایمان", "دکتر توکلی", 1, ""),
    ("karvarzi", "اورژانس", "دکتر جعفری", 2, ""),
    ("karvarzi", "روان‌پزشکی", "دکتر حیدری", 2, ""),
    ("karvarzi", "بیماری‌های عفونی", "دکتر مرادی", 7, ""),
    ("karvarzi", "قلب و عروق", "دکتر هاشمی", 2, ""),
    ("karvarzi", "مغز و اعصاب", "دکتر حیدری", 5, ""),
    ("karvarzi", "ارتوپدی", "دکتر توکلی", 7, ""),
    ("karvarzi", "اورولوژی", "دکتر شهیدی", 2, ""),
    ("karvarzi", "چشم‌پزشکی", "دکتر جعفری", 1, ""),
    ("karvarzi", "گوش، حلق و بینی", "دکتر حیدری", 1, ""),
    ("karvarzi", "پوست", "دکتر توکلی", 4, ""),
    ("karvarzi", "رادیولوژی", "دکتر مرادی", 4, ""),
    ("karvarzi", "بیهوشی", "دکتر امینی", 1, ""),
    ("karvarzi", "پزشکی قانونی", "دکتر کاظمی", 8, ""),
    ("karvarzi", "پزشکی اجتماعی", "دکتر توکلی", 7, ""),
    ("general", "معارف و اندیشه اسلامی", "دکتر شریفی", 7, ""),
    ("general", "زبان و ادبیات", "دکتر سعیدی", 7, ""),
)


class Command(BaseCommand):
    help = "Create or update the approved 75-lesson academic catalog."

    @transaction.atomic
    def handle(self, *args, **options):
        keys = [(section_slug, title) for section_slug, title, *_ in LESSONS]
        if len(LESSONS) != 75 or len(set(keys)) != len(keys):
            raise CommandError("The academic seed must contain 75 distinct section/title pairs.")

        section_counts = {"created": 0, "updated": 0}
        professor_created = 0
        lesson_counts = {"created": 0, "updated": 0}

        sections = {}
        for order, (slug, title, description) in enumerate(SECTIONS, start=1):
            section, created = Section.objects.update_or_create(
                slug=slug,
                defaults={"title": title, "description": description, "order": order},
            )
            # Serialize concurrent runs before resolving professors or lessons.
            sections[slug] = Section.objects.select_for_update().get(pk=section.pk)
            section_counts["created" if created else "updated"] += 1

        professors = {}
        for section_slug, title, professor_name, term, code in LESSONS:
            name = professor_name.strip()
            professor = professors.get(name)
            if professor is None:
                matches = list(Professor.objects.filter(name=name).order_by("pk")[:2])
                if len(matches) > 1:
                    raise CommandError(f"Professor name is ambiguous: {name}")
                professor = matches[0] if matches else Professor.objects.create(name=name)
                if not matches:
                    professor_created += 1
                professors[name] = professor

            try:
                _, created = Lesson.objects.update_or_create(
                    section=sections[section_slug],
                    title=title,
                    defaults={"professor": professor, "term": term, "code": code},
                )
            except Lesson.MultipleObjectsReturned as exc:
                raise CommandError(
                    f"Lesson identity is ambiguous: {section_slug}/{title}"
                ) from exc
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
