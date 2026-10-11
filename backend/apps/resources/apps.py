from django.apps import AppConfig


class ResourcesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.resources"
    label = "resources"

    def ready(self):
        from . import signals  # noqa: F401
