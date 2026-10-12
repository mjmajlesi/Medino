"""Synchronize the approved catalog represented by docs/lessons-seed.json."""

from collections import defaultdict

from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.db.models import Count

from apps.academics.models import Lesson, Professor, Section
from apps.resources.models import Resource


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
    help = "Synchronize the approved catalog; prune stale rows only with --prune."

    def add_arguments(self, parser):
        parser.add_argument(
            "--prune", action="store_true", help="Delete stale lessons without resources and unused professors."
        )
        parser.add_argument(
            "--dry-run", action="store_true", help="Show planned changes without writing to the database."
        )

    def _plan(self, prune):
        keys = [(section_slug, title) for section_slug, title, *_ in LESSONS]
        if len(LESSONS) != 75 or len(set(keys)) != len(keys):
            raise CommandError("The academic seed must contain 75 distinct section/title pairs.")

        existing_sections = {section.slug: section for section in Section.objects.all()}
        section_creates = []
        section_updates = []
        for order, (slug, title, description) in enumerate(SECTIONS, start=1):
            section = existing_sections.get(slug)
            if section is None:
                section_creates.append(slug)
            elif (section.title, section.description, section.order) != (title, description, order):
                section_updates.append(slug)

        professors_by_name = defaultdict(list)
        for professor in Professor.objects.all():
            professors_by_name[professor.name].append(professor)
        required_names = {professor_name.strip() for _, _, professor_name, _, _ in LESSONS}
        for name in required_names:
            if len(professors_by_name[name]) > 1:
                raise CommandError(f"Professor name is ambiguous: {name}")
        professor_creates = sorted(name for name in required_names if not professors_by_name[name])

        existing_lessons = list(
            Lesson.objects.select_related("section", "professor")
            .annotate(resource_count=Count("resources"))
            .order_by("pk")
        )
        lessons_by_key = defaultdict(list)
        for lesson in existing_lessons:
            lessons_by_key[(lesson.section.slug, lesson.title)].append(lesson)
        lesson_creates = []
        lesson_updates = []
        for section_slug, title, professor_name, term, code in LESSONS:
            matches = lessons_by_key[(section_slug, title)]
            if len(matches) > 1:
                raise CommandError(f"Lesson identity is ambiguous: {section_slug}/{title}")
            row = (section_slug, title, professor_name.strip(), term, code)
            if not matches:
                lesson_creates.append(row)
            else:
                lesson = matches[0]
                if (lesson.professor.name, lesson.term, lesson.code) != row[2:]:
                    lesson_updates.append((row, lesson))

        final_keys = set(keys)
        stale_lessons = [
            lesson for lesson in existing_lessons
            if (lesson.section.slug, lesson.title) not in final_keys
        ]
        safe_lessons = [lesson for lesson in stale_lessons if lesson.resource_count == 0]
        blocked_lessons = [lesson for lesson in stale_lessons if lesson.resource_count > 0]
        blocked_professor_ids = {lesson.professor_id for lesson in blocked_lessons}
        safe_professors = [
            professor for rows in professors_by_name.values() for professor in rows
            if professor.name not in required_names and professor.pk not in blocked_professor_ids
        ]
        safe_professors.sort(key=lambda professor: professor.pk)

        return {
            "sections": existing_sections,
            "section_creates": section_creates,
            "section_updates": section_updates,
            "professors": professors_by_name,
            "professor_creates": professor_creates,
            "lessons_by_key": lessons_by_key,
            "lesson_creates": lesson_creates,
            "lesson_updates": lesson_updates,
            "safe_lessons": safe_lessons,
            "blocked_lessons": blocked_lessons,
            "safe_professors": safe_professors,
            "expected_sections": len(existing_sections) + len(section_creates),
            "expected_professors": Professor.objects.count() + len(professor_creates) - (
                len(safe_professors) if prune else 0
            ),
            "expected_lessons": len(existing_lessons) + len(lesson_creates) - (
                len(safe_lessons) if prune else 0
            ),
        }

    def _print_plan(self, plan, prune):
        self.stdout.write("DRY RUN: no database writes.")
        self.stdout.write(
            f"Sections to create: {len(plan['section_creates'])}; "
            f"sections to update: {len(plan['section_updates'])}; "
            f"professors to create: {len(plan['professor_creates'])}."
        )
        for label, rows in (
            ("Lessons to create", plan["lesson_creates"]),
            ("Lessons to update", [row for row, _ in plan["lesson_updates"]]),
        ):
            self.stdout.write(f"{label} ({len(rows)}):")
            for slug, title, professor_name, term, code in rows:
                self.stdout.write(f"  {slug}/{title} -> {professor_name}, term {term}, code {code or '-'}")
        if prune:
            self.stdout.write(f"Stale lessons safe to delete ({len(plan['safe_lessons'])}):")
            for lesson in plan["safe_lessons"]:
                self.stdout.write(
                    f"  id {lesson.pk}: {lesson.section.slug}/{lesson.title}; resources 0"
                )
            self.stdout.write(
                f"Stale lessons blocked by resources ({len(plan['blocked_lessons'])}):"
            )
            for lesson in plan["blocked_lessons"]:
                self.stdout.write(
                    f"  id {lesson.pk}: {lesson.section.slug}/{lesson.title}; "
                    f"resources {lesson.resource_count}"
                )
            self.stdout.write(f"Professors safe to delete ({len(plan['safe_professors'])}):")
            for professor in plan["safe_professors"]:
                self.stdout.write(f"  id {professor.pk}: {professor.name}")
        self.stdout.write(
            f"Expected final counts: Sections {plan['expected_sections']}; "
            f"Professors {plan['expected_professors']}; Lessons {plan['expected_lessons']}."
        )
        if prune and plan["blocked_lessons"]:
            self.stdout.write(
                f"PRUNE INCOMPLETE: {len(plan['blocked_lessons'])} stale lessons have resources."
            )

    def handle(self, *args, **options):
        prune = options["prune"]
        if options["dry_run"]:
            self._print_plan(self._plan(prune), prune)
            return

        with transaction.atomic():
            # Serialize seed executions. Prune also locks existing lessons before
            # counting resources so a concurrent upload cannot be cascaded away.
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock(73922, 1)")
            if prune:
                list(Lesson.objects.select_for_update(of=("self",)).order_by("pk").values_list("pk", flat=True))
            plan = self._plan(prune)

            sections = plan["sections"]
            for order, (slug, title, description) in enumerate(SECTIONS, start=1):
                section = sections.get(slug)
                if section is None:
                    sections[slug] = Section.objects.create(
                        slug=slug, title=title, description=description, order=order
                    )
                elif slug in plan["section_updates"]:
                    section.title, section.description, section.order = title, description, order
                    section.save(update_fields=["title", "description", "order"])

            professors = {}
            for name in sorted({name.strip() for _, _, name, _, _ in LESSONS}):
                matches = plan["professors"][name]
                professors[name] = matches[0] if matches else Professor.objects.create(name=name)

            updated_keys = {(row[0], row[1]) for row, _ in plan["lesson_updates"]}
            for slug, title, name, term, code in LESSONS:
                matches = plan["lessons_by_key"][(slug, title)]
                if not matches:
                    Lesson.objects.create(
                        section=sections[slug], title=title, professor=professors[name.strip()],
                        term=term, code=code,
                    )
                elif (slug, title) in updated_keys:
                    lesson = matches[0]
                    lesson.professor = professors[name.strip()]
                    lesson.term = term
                    lesson.code = code
                    lesson.save(update_fields=["professor", "term", "code"])

            deleted_lessons = 0
            deleted_professors = 0
            if prune:
                for lesson in plan["safe_lessons"]:
                    if Resource.objects.filter(lesson_id=lesson.pk).exists():
                        raise CommandError(
                            f"Resource appeared on stale Lesson {lesson.pk}; pruning rolled back."
                        )
                    lesson.delete()
                    deleted_lessons += 1
                for professor in plan["safe_professors"]:
                    if Lesson.objects.filter(professor=professor).exists():
                        raise CommandError(
                            f"Professor {professor.pk} is still referenced; pruning rolled back."
                        )
                    professor.delete()
                    deleted_professors += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Sections: {len(SECTIONS)} (created {len(plan['section_creates'])}, "
                    f"updated {len(plan['section_updates'])}); "
                    f"Professors: {len({name for _, _, name, _, _ in LESSONS})} "
                    f"(created {len(plan['professor_creates'])}, deleted {deleted_professors}); "
                    f"Lessons: {len(LESSONS)} (created {len(plan['lesson_creates'])}, "
                    f"updated {len(plan['lesson_updates'])}, deleted {deleted_lessons})."
                )
            )
            self.stdout.write(
                f"Final counts: Sections {Section.objects.count()}; "
                f"Professors {Professor.objects.count()}; Lessons {Lesson.objects.count()}."
            )
            if prune and plan["blocked_lessons"]:
                for lesson in plan["blocked_lessons"]:
                    self.stdout.write(
                        f"BLOCKED stale Lesson id {lesson.pk}: {lesson.section.slug}/{lesson.title}; "
                        f"resources {lesson.resource_count}"
                    )
                self.stdout.write(
                    f"PRUNE INCOMPLETE: {len(plan['blocked_lessons'])} stale lessons have resources."
                )
