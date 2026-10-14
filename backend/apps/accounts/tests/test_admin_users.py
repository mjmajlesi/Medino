from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken


User = get_user_model()


class AdminUsersAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = User.objects.create_user(
            student_no="402130433", password="StrongPass!2026", first_name="سارا",
            last_name="احمدی", entry_year=1402, current_term=5,
        )
        cls.other_student = User.objects.create_user(
            student_no="403765432", password="StrongPass!2026", first_name="علی",
            last_name="رضایی",
        )
        cls.staff = User.objects.create_user(
            student_no="400000001", password="StrongPass!2026", first_name="مدیر",
            is_staff=True,
        )
        cls.other_staff = User.objects.create_user(
            student_no="400000002", password="StrongPass!2026", is_staff=True,
        )
        cls.superuser = User.objects.create_superuser(
            student_no="400000003", password="StrongPass!2026"
        )
        cls.other_superuser = User.objects.create_superuser(
            student_no="400000004", password="StrongPass!2026"
        )

    def setUp(self):
        self.client = APIClient()
        self.list_url = reverse("admin-users")

    def authenticate(self, user):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(user)}")

    def access_url(self, user):
        return reverse("admin-user-access", args=[user.pk])

    def test_list_requires_active_staff_and_allows_superusers(self):
        self.assertEqual(self.client.get(self.list_url).status_code, 401)
        self.authenticate(self.student)
        self.assertEqual(self.client.get(self.list_url).status_code, 403)
        for user in (self.staff, self.superuser):
            with self.subTest(user=user.student_no):
                self.authenticate(user)
                self.assertEqual(self.client.get(self.list_url).status_code, 200)

        inactive = User.objects.create_user(
            student_no="400000005", password="StrongPass!2026", is_staff=True, is_active=False
        )
        self.authenticate(inactive)
        self.assertEqual(self.client.get(self.list_url).status_code, 401)

    def test_list_returns_only_safe_fields_and_string_ids(self):
        self.authenticate(self.staff)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.data), {"count", "next", "previous", "results"})
        self.assertEqual(response.data["count"], 6)
        expected = {
            "id", "student_no", "first_name", "last_name", "entry_year",
            "current_term", "is_active", "is_staff", "is_superuser",
        }
        self.assertTrue(all(set(item) == expected for item in response.data["results"]))
        student = next(item for item in response.data["results"] if item["id"] == str(self.student.pk))
        student_json = next(item for item in response.json()["results"] if item["id"] == str(self.student.pk))
        self.assertEqual(student["entry_year"], 1402)
        self.assertEqual(student["current_term"], 5)
        self.assertIs(type(student_json["entry_year"]), int)
        self.assertIs(type(student_json["current_term"]), int)
        self.assertFalse(student["is_staff"])
        self.assertFalse(student["is_superuser"])
        other = next(item for item in response.json()["results"] if item["id"] == str(self.other_student.pk))
        self.assertIsNone(other["entry_year"])
        self.assertIsNone(other["current_term"])
        self.assertNotIn(self.student.password, str(response.data))

    def test_searches_student_number_and_names(self):
        self.authenticate(self.staff)
        for search, expected_id in (
            ("130433", self.student.pk),
            ("سارا", self.student.pk),
            ("احمدی", self.student.pk),
            ("رضایی", self.other_student.pk),
        ):
            with self.subTest(search=search):
                response = self.client.get(self.list_url, {"search": f" {search} "})
                self.assertEqual(response.status_code, 200)
                self.assertEqual([item["id"] for item in response.data["results"]], [str(expected_id)])
        self.other_student.first_name = "Alice"
        self.other_student.save(update_fields=["first_name"])
        response = self.client.get(self.list_url, {"search": "aLiCe"})
        self.assertEqual(response.data["results"][0]["id"], str(self.other_student.pk))

    def test_role_filter_and_invalid_role(self):
        self.authenticate(self.staff)
        expected = {
            "all": {self.student.pk, self.other_student.pk, self.staff.pk, self.other_staff.pk,
                    self.superuser.pk, self.other_superuser.pk},
            "student": {self.student.pk, self.other_student.pk},
            "staff": {self.staff.pk, self.other_staff.pk},
            "superuser": {self.superuser.pk, self.other_superuser.pk},
        }
        for role, ids in expected.items():
            with self.subTest(role=role):
                response = self.client.get(self.list_url, {"role": role})
                self.assertEqual(response.status_code, 200)
                self.assertEqual({item["id"] for item in response.data["results"]}, {str(pk) for pk in ids})
        self.assertEqual(self.client.get(self.list_url).data["count"], 6)
        invalid = self.client.get(self.list_url, {"role": "administrator"})
        self.assertEqual(invalid.status_code, 400)
        self.assertIn("role", invalid.data)

    def test_pagination_is_endpoint_local_with_stable_pages(self):
        User.objects.bulk_create([
            User(student_no=f"405{i:06d}") for i in range(20)
        ])
        self.authenticate(self.staff)
        first = self.client.get(self.list_url)
        second = self.client.get(self.list_url, {"page": 2})
        self.assertEqual(first.data["count"], 26)
        self.assertEqual(len(first.data["results"]), 20)
        self.assertEqual(len(second.data["results"]), 6)
        self.assertIsNotNone(first.data["next"])
        self.assertIsNotNone(second.data["previous"])
        self.assertFalse(
            {item["id"] for item in first.data["results"]}
            & {item["id"] for item in second.data["results"]}
        )

    def test_access_requires_staff_and_handles_unknown_user(self):
        url = self.access_url(self.student)
        self.assertEqual(self.client.patch(url, {"is_staff": True}, format="json").status_code, 401)
        self.authenticate(self.student)
        self.assertEqual(self.client.patch(url, {"is_staff": True}, format="json").status_code, 403)
        self.authenticate(self.staff)
        self.assertEqual(self.client.patch(reverse("admin-user-access", args=[999999]),
                                           {"is_staff": True}, format="json").status_code, 404)
        self.student.refresh_from_db()
        self.assertFalse(self.student.is_staff)

    def test_staff_can_grant_and_revoke_other_staff(self):
        self.authenticate(self.staff)
        grant = self.client.patch(self.access_url(self.student), {"is_staff": True}, format="json")
        self.assertEqual(grant.status_code, 200)
        self.assertEqual(grant.data["id"], str(self.student.pk))
        self.assertIs(type(grant.json()["entry_year"]), int)
        self.assertIs(type(grant.json()["current_term"]), int)
        self.assertTrue(grant.data["is_staff"])
        self.assertNotIn("password", grant.data)
        self.student.refresh_from_db()
        self.assertTrue(self.student.is_staff)
        self.assertFalse(self.student.is_superuser)

        revoke = self.client.patch(self.access_url(self.other_staff), {"is_staff": False}, format="json")
        self.assertEqual(revoke.status_code, 200)
        self.assertIsNone(revoke.json()["entry_year"])
        self.assertIsNone(revoke.json()["current_term"])
        self.other_staff.refresh_from_db()
        self.assertFalse(self.other_staff.is_staff)
        self.assertFalse(self.other_staff.is_superuser)

    def test_superuser_can_grant_and_revoke_non_superusers(self):
        self.authenticate(self.superuser)
        grant = self.client.patch(self.access_url(self.student), {"is_staff": True}, format="json")
        self.assertEqual(grant.status_code, 200)
        revoke = self.client.patch(self.access_url(self.other_staff), {"is_staff": False}, format="json")
        self.assertEqual(revoke.status_code, 200)
        self.student.refresh_from_db()
        self.other_staff.refresh_from_db()
        self.assertTrue(self.student.is_staff)
        self.assertFalse(self.other_staff.is_staff)

    def test_no_one_can_modify_superuser_or_revoke_self(self):
        for actor in (self.staff, self.superuser):
            with self.subTest(actor=actor.student_no):
                self.authenticate(actor)
                for value in (False, True):
                    response = self.client.patch(
                        self.access_url(self.other_superuser), {"is_staff": value}, format="json"
                    )
                    self.assertEqual(response.status_code, 403)
                    self.assertIn("Superuser access", response.data["detail"])
        self.authenticate(self.superuser)
        self.assertEqual(self.client.patch(
            self.access_url(self.superuser), {"is_staff": False}, format="json"
        ).status_code, 403)
        self.other_superuser.refresh_from_db()
        self.assertTrue(self.other_superuser.is_staff)
        self.assertTrue(self.other_superuser.is_superuser)

        self.authenticate(self.staff)
        response = self.client.patch(self.access_url(self.staff), {"is_staff": False}, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertIn("your own admin access", response.data["detail"])
        self.staff.refresh_from_db()
        self.assertTrue(self.staff.is_staff)

    def test_access_payload_is_exactly_is_staff_and_never_promotes(self):
        self.authenticate(self.staff)
        for field, value in (
            ("is_superuser", True), ("password", "UnsafePass!2026"),
            ("student_no", "999999999"), ("is_active", False),
            ("first_name", "Changed"), ("last_name", "Changed"),
            ("entry_year", 1400), ("current_term", 2),
            ("groups", [1]), ("user_permissions", [1]), ("unknown", "value"),
        ):
            with self.subTest(field=field):
                response = self.client.patch(
                    self.access_url(self.student), {"is_staff": True, field: value}, format="json"
                )
                self.assertEqual(response.status_code, 400)
                self.assertIn(field, response.data)
                self.student.refresh_from_db()
                self.assertFalse(self.student.is_staff)
                self.assertFalse(self.student.is_superuser)
        for payload in ({}, {"is_staff": "invalid"}):
            response = self.client.patch(self.access_url(self.student), payload, format="json")
            self.assertEqual(response.status_code, 400)

