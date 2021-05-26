from django.shortcuts import render, get_object_or_404
from rest_framework import generics, mixins

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.exceptions import NotFound
from rest_framework.decorators import action
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import APIException

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
    ContributorChoiceSerializer,
    IssueSerializer,
    CommentSerializer,
)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing project instances.
    """
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return self.request.user.projects.all()  # Only projects of authenticated user

    def list(self, request):
        queryset = self.get_queryset()
        serializer = ProjectSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        project = get_object_or_404(queryset, pk=pk)
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # serializer = ProjectSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)

        data = request.data
        user = request.user

        new_project = Project.objects.create(
            title=data["title"], description=data['description'], project_type=data["project_type"])

        new_project.save()
        contributor = Contributor.objects.create(project=new_project, user=user, permission="Author")

        # serializer = ProjectSerializer(new_project)
        serializer = ContributorSerializer(contributor)  # Display contributor serializer or project?

        return Response(serializer.data)


class UserViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
):
    """
    A viewset for viewing and editing issue instances.
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        else:
            return ContributorChoiceSerializer

    def list(self, request, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)
        users = project.users.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def create(self, request, project_pk=None):
        # How to control input, e.g. must correspond to choice pre-defined?
        data = request.data
        required_user = "user_choice"
        required_permission = "permission"
        if required_user in data and required_permission in data:
            user_choice = data.get(required_user)
            permission_choice = data.get(required_permission)
            user_email = user_choice  # This test for email, must to generate
            print(user_email)
            user = get_object_or_404(User, email=user_email)
            project = get_object_or_404(Project, pk=project_pk)

            contributor = Contributor.objects.create(user=user, project=project, permission=permission_choice)
            serializer = ContributorSerializer(contributor)
            return Response(serializer.data)

        else:
            raise APIException("Must fill 'user_choice' and 'permission' fields!")


    def retrieve(self, request, pk=None, project_pk=None):
        queryset = User.objects.filter(pk=pk, projects=project_pk)
        user = get_object_or_404(queryset, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def destroy(self, request, pk=None, project_pk=None):
        contributor = get_object_or_404(Contributor, user=pk, project=project_pk)
        contributor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IssueViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing issue instances.
    """
    serializer_class = IssueSerializer
    queryset = Issue.objects.all()


    def list(self, request, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)
        issues = project.issues.all()
        serializer = IssueSerializer(issues, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, project_pk=None):
        queryset = Issue.objects.filter(pk=pk, project=project_pk)
        issue = get_object_or_404(queryset, pk=pk)
        serializer = IssueSerializer(issue)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing comment instances.
    """
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    def list(self, request, project_pk=None, issue_pk=None):
        issue = get_object_or_404(Issue, pk=issue_pk)
        comments = issue.comments.all()

        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class ContributorViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing contributor instances.
    """
    # permission_classes = ()
    serializer_class = ContributorSerializer
    queryset = Contributor.objects.all()
