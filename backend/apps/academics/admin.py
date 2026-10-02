from django.contrib import admin

from .models import Lesson, Professor, Section


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "order")
    search_fields = ("title", "slug")
    ordering = ("order", "id")


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "section", "professor", "term", "code")
    list_filter = ("section", "term")
    search_fields = ("title", "professor__name", "code")
    list_select_related = ("section", "professor")
