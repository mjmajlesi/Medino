from django.db import models


class Section(models.Model):
    slug = models.SlugField(max_length=32, unique=True)
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ("order", "id")

    def __str__(self):
        return self.title


class Professor(models.Model):
    name = models.CharField(max_length=150)

    class Meta:
        ordering = ("name", "id")

    def __str__(self):
        return self.name


class Lesson(models.Model):
    section = models.ForeignKey(Section, on_delete=models.PROTECT, related_name="lessons")
    title = models.CharField(max_length=200)
    professor = models.ForeignKey(
        Professor, on_delete=models.PROTECT, related_name="lessons"
    )
    term = models.PositiveIntegerField()
    code = models.CharField(max_length=32, blank=True)

    class Meta:
        ordering = ("section__order", "id")
        constraints = [
            models.UniqueConstraint(
                fields=("section", "title", "professor", "term"),
                name="unique_lesson_section_title_professor_term",
            )
        ]

    def __str__(self):
        return self.title
