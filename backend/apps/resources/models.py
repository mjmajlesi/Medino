from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Resource(models.Model):
    class Type(models.TextChoices):
        NOTE = "note", "Note"
        VIDEO = "video", "Video"
        SAMPLE = "sample", "Sample exam"
        SUMMARY = "summary", "Summary"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    lesson = models.ForeignKey(
        "academics.Lesson", on_delete=models.PROTECT, related_name="resources"
    )
    type = models.CharField(max_length=10, choices=Type.choices)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="resources/", blank=True)
    external_url = models.URLField(blank=True)
    duration = models.CharField(max_length=20, blank=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="uploaded_resources",
        null=True,
        blank=True,
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="reviewed_resources",
        null=True,
        blank=True,
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("created_at", "id")
        indexes = [
            models.Index(fields=("lesson", "status"), name="resource_lesson_status_idx"),
            models.Index(fields=("status", "type"), name="resource_status_type_idx"),
        ]

    def clean(self):
        super().clean()
        if not self.title or not self.title.strip():
            raise ValidationError({"title": "A title is required."})
        if bool(self.file) == bool(self.external_url):
            raise ValidationError(
                "Provide exactly one source: an uploaded file or an external URL."
            )
        if self.external_url and not self.external_url.startswith(("https://", "http://")):
            raise ValidationError({"external_url": "Use an HTTP or HTTPS URL."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title
