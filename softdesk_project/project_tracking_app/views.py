from django.shortcuts import render, get_object_or_404

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.exceptions import NotFound
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    User,
    Project,
    Contributor,
    Issue,
    Comment,
)
from .serializers import (
    UserSerializer,
    ProjectSerializer,
    ContributorSerializer,
    IssueSerializer,
    CommentSerializer,
)


class ProjectViewSet(viewsets.ModelViewSet):
    # class ProjectViewSet(viewsets.ViewSet):
    """
    A viewset for viewing and editing project instances.
    """
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()


    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.user

        new_project = Project.objects.create(
            title=data["title"], description=data['description'], project_type=data["project_type"])

        new_project.save()

        for user in data["users"]:
            user_obj = User.objects.get(email=user["email"])
            new_project.users.add(user_obj)

        serializer = ProjectSerializer(new_project)

        return Response(serializer.data)

    # def create(self, request, *args, **kwargs):
    #     many = True if isinstance(request.data, list) else False
    #     serializer = ProjectSerializer(data=request.data, many=many)
    #     serializer.is_valid(raise_exception=True)
    #     user = request.user  # you can change here
    #     project_list = [Project(**data, user=user) for data in serializer.validated_data]
    #     Project.objects.bulk_create(project_list)
    #     return Response({}, status=status.HTTP_201_CREATED)

    # def create(self, request, *args, **kwargs):
    #     many = True if isinstance(request.data, list) else False
    #     serializer = ProjectSerializer(data=request.data, many=many)
    #     serializer.is_valid(raise_exception=True)
    #     author = request.user  # you can change here
    #     project_list = [Project(**data, author=author) for data in serializer.validated_data]
    #     Project.objects.bulk_create(project_list)
    #     return Response({}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    # @action(detail=True, methods=['get', 'post'])
    def users(self, request, pk=None):
        project = get_object_or_404(Project, pk=pk)
        users = project.users.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class IssueViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing issue instances.
    """
    serializer_class = IssueSerializer
    queryset = Issue.objects.all()


class CommentViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing comment instances.
    """
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()


class ContributorViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing contributor instances.
    """
    permission_classes = ()
    serializer_class = ContributorSerializer
    queryset = Contributor.objects.all()
