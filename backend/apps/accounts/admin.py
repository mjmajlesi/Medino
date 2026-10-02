from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class MedinoUserAdmin(UserAdmin):
    list_display = (
        "student_no",
        "first_name",
        "last_name",
        "entry_year",
        "current_term",
        "is_staff",
        "is_active",
    )
    search_fields = ("student_no", "first_name", "last_name")
    ordering = ("student_no",)
    fieldsets = (
        (None, {"fields": ("student_no", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email", "entry_year", "current_term")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("student_no", "password1", "password2")}),
    )
