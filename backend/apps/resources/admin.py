from django.contrib import admin

from .models import Resource


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "lesson", "type", "status", "uploaded_by", "created_at")
    list_filter = ("type", "status", "lesson__section")
    search_fields = (
        "title",
        "lesson__title",
        "lesson__professor__name",
        "uploaded_by__first_name",
        "uploaded_by__last_name",
    )
    list_select_related = ("lesson", "uploaded_by")
