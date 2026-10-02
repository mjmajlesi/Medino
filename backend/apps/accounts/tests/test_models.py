from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase


class UserModelTests(TestCase):
    def test_student_number_is_identity_and_unique(self):
        user_model = get_user_model()
        self.assertEqual(user_model.USERNAME_FIELD, "student_no")

        user = user_model.objects.create_user(student_no="001234", password="safe-password")
        self.assertEqual(user.student_no, "001234")
        self.assertTrue(user.check_password("safe-password"))

        with self.assertRaises(IntegrityError), transaction.atomic():
            user_model.objects.create_user(student_no="001234", password="another-password")
