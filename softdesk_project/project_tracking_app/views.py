from django.shortcuts import get_object_or_404
from django.template.backends import django
from rest_framework import generics, mixins

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from django.db import IntegrityError

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
        permission = "AUTHOR"
        serializer = ProjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        project = serializer.create()

        contributor = Contributor.objects.create(project=project, user=request.user, permission=permission)
        serializer = ContributorSerializer(contributor)

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


    def list(self, request, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)
        users = project.users.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def create(self, request, project_pk=None):
        # How to control input, e.g. must correspond to choice pre-defined?
        try:
            data = request.data
            project_data = {"project": project_pk}
            data = {**data, **project_data}
            serializer = ContributorSerializer(data=data)
            serializer.is_valid() # Why always False ???
            serializer.errors
            serializer.save()
        except IntegrityError:
            raise APIException("The user is already added to this project.")

        return Response(serializer.data)

    def retrieve(self, request, pk=None, project_pk=None):
        queryset = User.objects.filter(pk=pk, projects=project_pk)
        user = get_object_or_404(queryset, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def destroy(self, request, pk=None, project_pk=None):
        contributor = get_object_or_404(Contributor, user=pk, project=project_pk)
        contributor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IssueViewSet(viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin
                   ):
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

    def create(self, request, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)
        serializer = IssueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.errors
        serializer.save(project=project)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, project_pk=None):
        queryset = Issue.objects.filter(pk=pk, project=project_pk)
        issue = get_object_or_404(queryset, pk=pk)
        serializer = IssueSerializer(issue)
        return Response(serializer.data)

    def perform_update(self, serializer):
        data = serializer.validated_data

        author_user_data = data.pop("author_user")
        author_user = get_object_or_404(User, **author_user_data)

        assignee_user_data = data.pop("assignee_user")
        assignee_user = get_object_or_404(User, **assignee_user_data)
        serializer.save(author_user=author_user, assignee_user=assignee_user)
        print(serializer.data)


class CommentViewSet(viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin
    ):
    """
    A viewset for viewing and editing comment instances.
    """
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()

    # def get_queryset(self, project_pk=None, issue_pk=None):
    #     issue = get_object_or_404(Issue, pk=issue_pk)
    #     comments = issue.comments.all()
    #     return comments

    def list(self, request, project_pk=None, issue_pk=None):
        issue = get_object_or_404(Issue, pk=issue_pk)
        comments = issue.comments.all()
        # comments = self.get_queryset(project_pk, issue_pk)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def create(self, request, project_pk=None, issue_pk=None):
        issue = get_object_or_404(Issue, pk=issue_pk)
        author_user = self.request.user
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.errors

        serializer.save(author_user=author_user, issue=issue)
        return Response(serializer.data)


    def retrieve(self, request, project_pk=None, issue_pk=None, pk=None):
        comment = get_object_or_404(Comment, issue=issue_pk, pk=pk)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    def destroy(self, request, project_pk=None, pk=None, issue_pk=None):
        comment = get_object_or_404(Comment, issue=issue_pk, pk=pk)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ContributorViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing contributor instances.
    """
    # permission_classes = ()
    serializer_class = ContributorSerializer
    queryset = Contributor.objects.all()
