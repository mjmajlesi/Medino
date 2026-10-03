from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Lesson, Section
from .serializers import LessonFilterSerializer, LessonSerializer, SectionSerializer
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
        filters = LessonFilterSerializer(data=self.request.query_params)
        filters.is_valid(raise_exception=True)
        values = filters.validated_data
        queryset = super().get_queryset()

        if values.get("section"):
            queryset = queryset.filter(section__slug=values["section"])
        if values.get("search"):
            term = values["search"]
            queryset = queryset.filter(
                Q(title__icontains=term) | Q(professor__name__icontains=term)
            )
        if values.get("professor"):
            queryset = queryset.filter(professor__name__icontains=values["professor"])
        if values.get("term") is not None:
            queryset = queryset.filter(term=values["term"])
        if values.get("type"):
            queryset = queryset.filter(
                resources__type=values["type"],
                resources__status=Resource.Status.APPROVED,
            ).distinct()
        if values.get("ordering"):
            queryset = queryset.order_by(values["ordering"], "-pk")
        return queryset


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
