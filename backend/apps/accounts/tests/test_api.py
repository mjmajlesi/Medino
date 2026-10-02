from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken


User = get_user_model()


class AccountsAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("auth-register")
        self.login_url = reverse("auth-login")
        self.refresh_url = reverse("auth-token-refresh")
        self.me_url = reverse("auth-me")
        self.payload = {
            "first_name": "محمد",
            "last_name": "جعفری",
            "student_no": "401123456",
            "entry_year": "1401",
            "current_term": "8",
            "password": "StrongPass!2026",
        }

    def create_student(self, **overrides):
        details = {
            "first_name": self.payload["first_name"],
            "last_name": self.payload["last_name"],
            "student_no": self.payload["student_no"],
            "entry_year": 1401,
            "current_term": 8,
            "password": self.payload["password"],
        }
        details.update(overrides)
        return User.objects.create_user(**details)

    def expected_user(self):
        return {key: self.payload[key] for key in (
            "first_name", "last_name", "student_no", "entry_year", "current_term"
        )}

    def test_registration_creates_normal_student_and_returns_tokens(self):
        response = self.client.post(self.register_url, self.payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["user"], self.expected_user())
        self.assertEqual(set(response.data), {"user", "access", "refresh"})
        user = User.objects.get(student_no=self.payload["student_no"])
        self.assertEqual(user.entry_year, 1401)
        self.assertEqual(user.current_term, 8)
        self.assertNotEqual(user.password, self.payload["password"])
        self.assertTrue(user.check_password(self.payload["password"]))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertEqual(AccessToken(response.data["access"])["user_id"], str(user.pk))
        self.assertEqual(RefreshToken(response.data["refresh"])["user_id"], str(user.pk))

    def test_registration_rejects_duplicate_and_missing_fields(self):
        self.create_student()
        duplicate = self.client.post(self.register_url, self.payload, format="json")
        self.assertEqual(duplicate.status_code, 400)
        self.assertIn("student_no", duplicate.data)

        for field in self.payload:
            with self.subTest(field=field):
                payload = {key: value for key, value in self.payload.items() if key != field}
                response = self.client.post(self.register_url, payload, format="json")
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)

    def test_registration_validates_numeric_fields_and_password(self):
        for field, value in (
            ("entry_year", "0"),
            ("entry_year", "not-a-year"),
            ("current_term", "-1"),
            ("current_term", "not-a-term"),
            ("password", "password"),
        ):
            with self.subTest(field=field, value=value):
                response = self.client.post(
                    self.register_url, {**self.payload, field: value}, format="json"
                )
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)

        response = self.client.post(
            self.register_url,
            {**self.payload, "entry_year": 1401, "current_term": 8},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["user"]["entry_year"], "1401")
        self.assertEqual(response.data["user"]["current_term"], "8")

    def test_registration_cannot_set_admin_fields(self):
        response = self.client.post(
            self.register_url,
            {
                **self.payload,
                "is_staff": True,
                "is_superuser": True,
                "is_active": False,
                "groups": [1],
                "user_permissions": [1],
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(student_no=self.payload["student_no"])
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertFalse(user.groups.exists())
        self.assertFalse(user.user_permissions.exists())
        self.assertEqual(response.data["user"], self.expected_user())

    def test_password_whitespace_is_preserved(self):
        password = " StrongPass!2026 "
        response = self.client.post(
            self.register_url, {**self.payload, "password": password}, format="json"
        )
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(student_no=self.payload["student_no"])
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.check_password(password.strip()))
        login = self.client.post(
            self.login_url,
            {"student_no": user.student_no, "password": password},
            format="json",
        )
        self.assertEqual(login.status_code, 200)

    def test_login_uses_student_number_and_returns_user_and_tokens(self):
        user = self.create_student()
        self.assertEqual(User.USERNAME_FIELD, "student_no")
        self.assertNotIn("username", [field.name for field in User._meta.fields])

        response = self.client.post(
            self.login_url,
            {"student_no": user.student_no, "password": self.payload["password"]},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user"], self.expected_user())
        self.assertEqual(AccessToken(response.data["access"])["user_id"], str(user.pk))
        self.assertEqual(RefreshToken(response.data["refresh"])["user_id"], str(user.pk))

    def test_login_rejects_wrong_unknown_and_inactive_with_same_error(self):
        user = self.create_student()
        responses = [
            self.client.post(
                self.login_url,
                {"student_no": user.student_no, "password": "wrong-password"},
                format="json",
            ),
            self.client.post(
                self.login_url,
                {"student_no": "unknown", "password": self.payload["password"]},
                format="json",
            ),
        ]
        user.is_active = False
        user.save(update_fields=["is_active"])
        responses.append(self.client.post(
            self.login_url,
            {"student_no": user.student_no, "password": self.payload["password"]},
            format="json",
        ))
        self.assertEqual([response.status_code for response in responses], [400, 400, 400])
        self.assertEqual(responses[0].data, responses[1].data)
        self.assertEqual(responses[1].data, responses[2].data)

    def test_me_requires_bearer_token_and_returns_only_its_user(self):
        user = self.create_student()
        other = self.create_student(student_no="401999999", first_name="Other")
        anonymous = self.client.get(self.me_url)
        self.assertEqual(anonymous.status_code, 401)

        access = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, self.expected_user())
        self.assertNotEqual(response.data["student_no"], other.student_no)
        self.assertEqual(set(response.data), set(self.expected_user()))

    def test_refresh_returns_new_access_and_rejects_invalid_token(self):
        user = self.create_student()
        refresh = RefreshToken.for_user(user)
        response = self.client.post(
            self.refresh_url, {"refresh": str(refresh)}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.data), {"access"})
        self.assertEqual(AccessToken(response.data["access"])["user_id"], str(user.pk))

        invalid = self.client.post(
            self.refresh_url, {"refresh": "invalid-token"}, format="json"
        )
        self.assertEqual(invalid.status_code, 401)

    def test_public_auth_endpoints_ignore_stale_bearer_header(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer stale-token")
        response = self.client.post(self.register_url, self.payload, format="json")
        self.assertEqual(response.status_code, 201)
        login = self.client.post(
            self.login_url,
            {"student_no": self.payload["student_no"], "password": self.payload["password"]},
            format="json",
        )
        self.assertEqual(login.status_code, 200)
