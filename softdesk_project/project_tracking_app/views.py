from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import (
    Project,
    Contributor,
    Issue,
    Comment,
)
from .serializers import(
    ProjectSerializer,
    ContributorSerializer,
    IssueSerializer,
    CommentSerializer,
)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing project instances.
    """
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
