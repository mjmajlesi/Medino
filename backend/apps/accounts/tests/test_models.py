from io import StringIO
from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import RequestFactory, TestCase

from apps.academics.models import Lesson, Professor, Section
from apps.resources.models import Resource


class UserModelTests(TestCase):
    def test_student_number_is_identity_and_unique(self):
        user_model = get_user_model()
        self.assertEqual(user_model.USERNAME_FIELD, "student_no")

        user = user_model.objects.create_user(student_no="001234", password="safe-password")
        self.assertEqual(user.student_no, "001234")
        self.assertTrue(user.check_password("safe-password"))

        with self.assertRaises(IntegrityError), transaction.atomic():
            user_model.objects.create_user(student_no="001234", password="another-password")

    def test_create_superuser_enforces_flags_and_hashes_password(self):
        user = get_user_model().objects.create_superuser(
            student_no="402131013", password="safe-admin-password"
        )

        self.assertEqual(user.student_no, "402131013")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertNotEqual(user.password, "safe-admin-password")
        self.assertTrue(user.check_password("safe-admin-password"))

    def test_createsuperuser_command_uses_the_custom_user_manager(self):
        with patch.dict("os.environ", {"DJANGO_SUPERUSER_PASSWORD": "safe-admin-password"}):
            call_command(
                "createsuperuser",
                interactive=False,
                student_no="402131013",
                stdout=StringIO(),
            )

        user = get_user_model().objects.get(student_no="402131013")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertTrue(user.check_password("safe-admin-password"))

    def test_create_superuser_rejects_disabled_privilege_flags(self):
        for field in ("is_staff", "is_superuser", "is_active"):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, field):
                get_user_model().objects.create_superuser(
                    student_no="402131013", password="safe-admin-password", **{field: False}
                )
        self.assertFalse(get_user_model().objects.filter(student_no="402131013").exists())

    def test_superuser_has_all_model_permissions_without_explicit_assignments(self):
        user = get_user_model().objects.create_superuser(
            student_no="402131013", password="safe-admin-password"
        )
        self.assertEqual(user.user_permissions.count(), 0)

        for model in (get_user_model(), Section, Professor, Lesson, Resource):
            for action in ("add", "change", "delete", "view"):
                permission = f"{model._meta.app_label}.{action}_{model._meta.model_name}"
                with self.subTest(permission=permission):
                    self.assertTrue(
                        Permission.objects.filter(
                            content_type__app_label=model._meta.app_label,
                            codename=f"{action}_{model._meta.model_name}",
                        ).exists()
                    )
                    self.assertTrue(user.has_perm(permission))

        for app_label in ("accounts", "academics", "resources"):
            with self.subTest(app_label=app_label):
                self.assertTrue(user.has_module_perms(app_label))
        self.assertEqual(user.user_permissions.count(), 0)

    def test_registered_admin_models_allow_superuser_management(self):
        user = get_user_model().objects.create_superuser(
            student_no="402131013", password="safe-admin-password"
        )
        request = RequestFactory().get("/admin/")
        request.user = user

        for model in (get_user_model(), Section, Professor, Lesson, Resource):
            model_admin = admin.site._registry[model]
            with self.subTest(model=model.__name__):
                self.assertTrue(model_admin.has_add_permission(request))
                self.assertTrue(model_admin.has_change_permission(request))
                self.assertTrue(model_admin.has_delete_permission(request))
                self.assertTrue(model_admin.has_view_permission(request))
