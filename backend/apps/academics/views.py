from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Lesson, Section
from .serializers import LessonSerializer, SectionSerializer
from apps.resources.models import Resource
from apps.resources.serializers import ResourceSerializer


class SectionListView(generics.ListAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    pagination_class = None
    queryset = Section.objects.all()
    serializer_class = SectionSerializer


class LessonListView(generics.ListAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    pagination_class = None
    queryset = Lesson.objects.select_related("section", "professor")
    serializer_class = LessonSerializer

    def get_queryset(self):
        unsupported = {"section", "search", "professor", "type", "term"}
        if unsupported.intersection(self.request.query_params):
            raise ValidationError({"detail": "Lesson filters are not available yet."})
        return super().get_queryset()


class LessonDetailView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, pk):
        lesson = get_object_or_404(
            Lesson.objects.select_related("section", "professor"), pk=pk
        )
        resources = Resource.objects.filter(
            lesson=lesson, status=Resource.Status.APPROVED
        ).select_related("uploaded_by")
        return Response(
            {
                "lesson": LessonSerializer(lesson).data,
                "resources": ResourceSerializer(
                    resources, many=True, context={"request": request}
                ).data,
            }
        )
