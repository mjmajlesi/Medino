from django.urls import path

from .views import LessonDetailView, LessonListView, SectionListView


urlpatterns = [
    path("sections/", SectionListView.as_view(), name="section-list"),
    path("lessons/", LessonListView.as_view(), name="lesson-list"),
    path("lessons/<int:pk>/", LessonDetailView.as_view(), name="lesson-detail"),
]
