from django.templatetags.static import static
from django.test import SimpleTestCase
from django.urls import Resolver404, resolve, reverse


class AdminRoutingTests(SimpleTestCase):
    def test_django_admin_has_a_distinct_path_from_react_admin(self):
        self.assertEqual(reverse("admin:index"), "/django-admin/")
        self.assertEqual(self.client.get("/django-admin/").status_code, 302)
        with self.assertRaises(Resolver404):
            resolve("/admin/")

    def test_collected_admin_static_uses_root_static_prefix(self):
        self.assertEqual(static("admin/css/base.css"), "/static/admin/css/base.css")
