"""Remove only the explicitly identified artifacts from a development database."""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.academics.models import Lesson, Professor
from apps.resources.models import Resource


class Command(BaseCommand):
    help = "Remove 499* users, E2E-TEST-UPLOAD resources, and unused Test Prof rows in DEBUG mode."

    def add_arguments(self, parser):
        parser.add_argument("--yes", action="store_true", help="Confirm deletion after reviewing the preview.")

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Development cleanup is disabled unless DEBUG=True.")

        user_model = get_user_model()
        users = list(user_model.objects.filter(student_no__startswith="499").order_by("student_no"))
        resources = list(Resource.objects.filter(title="E2E-TEST-UPLOAD").order_by("pk"))
        test_professors = list(Professor.objects.filter(name="Test Prof").order_by("pk"))
        user_ids = [user.pk for user in users]
        resource_ids = [resource.pk for resource in resources]
        retained_resources = Resource.objects.exclude(pk__in=resource_ids)

        self.stdout.write(f"499* users to delete ({len(users)}):")
        for user in users:
            self.stdout.write(f"  {user.student_no} (id {user.pk})")
        self.stdout.write(
            "Retained resources losing 499* user attribution: "
            f"{retained_resources.filter(uploaded_by_id__in=user_ids).count()} uploads, "
            f"{retained_resources.filter(reviewed_by_id__in=user_ids).count()} reviews"
        )
        self.stdout.write(f"E2E-TEST-UPLOAD resources to delete ({len(resources)}):")
        for resource in resources:
            self.stdout.write(f"  id {resource.pk} (stored file: {'yes' if resource.file else 'no'})")
        self.stdout.write(f"Test Prof rows to examine ({len(test_professors)}):")
        for professor in test_professors:
            references = Lesson.objects.filter(professor=professor).count()
            self.stdout.write(f"  id {professor.pk} (referenced by {references} lessons)")

        if not options["yes"]:
            raise CommandError("Review the preview, then pass --yes to delete these development artifacts.")

        with transaction.atomic():
            Resource.objects.filter(pk__in=resource_ids).delete()
            user_model.objects.filter(pk__in=user_ids).delete()
            deleted_professors = 0
            for professor in test_professors:
                if not Lesson.objects.filter(professor=professor).exists():
                    professor.delete()
                    deleted_professors += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Deleted {len(users)} users, {len(resources)} resources, "
                f"and {deleted_professors} unused Test Prof rows."
            )
        )
