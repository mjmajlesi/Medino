from unittest.mock import patch

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from config.settings import env_bool, env_list, env_nonnegative_int, required_env


class EnvironmentSettingsTests(SimpleTestCase):
    def test_postgresql_is_required_for_application_and_tests(self):
        self.assertEqual(settings.DATABASES["default"]["ENGINE"], "django.db.backends.postgresql")
        for key in ("NAME", "USER", "PASSWORD", "HOST", "PORT"):
            self.assertTrue(settings.DATABASES["default"][key])

    def test_required_values_cannot_be_blank_and_lists_trim_whitespace(self):
        with patch.dict("os.environ", {"POSTGRES_DB": "  "}):
            with self.assertRaises(ImproperlyConfigured):
                required_env("POSTGRES_DB")
        with patch.dict("os.environ", {"ALLOWED_HOSTS": " localhost, , 127.0.0.1 "}):
            self.assertEqual(env_list("ALLOWED_HOSTS"), ["localhost", "127.0.0.1"])

    def test_security_flag_and_hsts_parsing(self):
        for value, expected in ((" YES ", True), ("1", True), ("false", False), ("arbitrary", False), ("", False)):
            with self.subTest(value=value), patch.dict("os.environ", {"SECURE_SSL_REDIRECT": value}):
                self.assertIs(env_bool("SECURE_SSL_REDIRECT"), expected)
        for value in ("-1", "invalid", ""):
            with self.subTest(value=value), patch.dict("os.environ", {"SECURE_HSTS_SECONDS": value}):
                with self.assertRaises(ImproperlyConfigured):
                    env_nonnegative_int("SECURE_HSTS_SECONDS", 0)
