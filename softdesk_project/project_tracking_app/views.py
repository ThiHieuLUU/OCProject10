import functools

from django.shortcuts import get_object_or_404
from rest_framework import mixins

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from django.db import IntegrityError

from rest_framework.viewsets import ModelViewSet
from rules.contrib.rest_framework import AutoPermissionViewSetMixin

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

from .nested_urls_permissions import UrlCheckDecorator

from .permissions import IssuePermission


class ProjectViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing project instances.
    """
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return self.request.user.projects.all()  # Only projects of authenticated user

    def create(self, request, *args, **kwargs):
        permission = "AUTHOR"
        serializer = ProjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        project = serializer.save()

        contributor = Contributor.objects.create(project=project, user=request.user, permission=permission)
        serializer = ContributorSerializer(contributor)

        return Response(serializer.data)


class ProjectUserViewSet(viewsets.ModelViewSet):
#     viewsets.GenericViewSet,
#     mixins.ListModelMixin,
#     mixins.CreateModelMixin,
#     mixins.DestroyModelMixin,
# ):
    """
    A viewset for viewing and editing issue instances.
    """
    serializer_class = UserSerializer

    def get_queryset(self):
        projects = self.request.user.projects.all()
        project_pk = self.kwargs["project_pk"]

        project = get_object_or_404(projects, pk=project_pk)
        users = project.users.all()
        return users

    def create(self, request, project_pk=None, *args, **kwargs):
        try:
            self.get_queryset()
            data = request.data
            user_data = data.pop('user')
            user_serializer = UserSerializer(data=user_data)
            user_serializer.is_valid()
            user = get_object_or_404(User, **user_serializer.data)

            project = get_object_or_404(Project, pk=project_pk)

            serializer = ContributorSerializer(data=data)  # data has popped user data
            serializer.is_valid()

            serializer.save(user=user, project=project)
        except IntegrityError:
            raise APIException("The user is already added to this project.")

        return Response(serializer.data)


    def destroy(self, request, project_pk=None, pk=None, *args, **kwargs):
        users = self.get_queryset()
        user = get_object_or_404(users, pk=pk)
        contributor = get_object_or_404(Contributor, user=user, project=project_pk)
        contributor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IssueViewSet(AutoPermissionViewSetMixin,
                   viewsets.GenericViewSet,
                   mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.UpdateModelMixin,
                   # IssuePermission,
                   ):
    """
    A viewset for viewing and editing issue instances.
    """
    # permission_required = 'read_project_issue_comment'
    serializer_class = IssueSerializer
    queryset = Issue.objects.all()
    # permission_classes = [IsAdminUser]
    permission_classes = [IssuePermission]
    # permission_classes = [IsAuthenticatedOrReadOnly]

    # def get_permissions(self):
    #     if self.action == 'update':
    #         return IsOwner()
    #     elif self.action == 'list':
    #         return IsAdminUser()
    #     else :
    #         return AllowAny()

    # @UrlCheckDecorator.check_url_project
    def list(self, request, project_pk=None, *args, **kwargs):
        project = get_object_or_404(Project, pk=project_pk)
        issues = project.issues.all()
        serializer = IssueSerializer(issues, many=True)
        return Response(serializer.data)

    def create(self, request, project_pk=None, *args, **kwargs):
        project = get_object_or_404(Project, pk=project_pk)
        author_user = self.request.user

        serializer = IssueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(project=project, author_user=author_user)
        return Response(serializer.data)

    def retrieve(self, request, project_pk=None, pk=None, *args, **kwargs):
        queryset = Issue.objects.filter(pk=pk, project=project_pk)
        issue = get_object_or_404(queryset, pk=pk)
        serializer = IssueSerializer(issue)
        return Response(serializer.data)

    def perform_update(self, serializer):
        data = serializer.validated_data

        assignee_user_data = data.pop("assignee_user")
        assignee_user = get_object_or_404(User, **assignee_user_data)
        serializer.save(assignee_user=assignee_user)


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

    def list(self, request, project_pk=None, issue_pk=None, *args, **kwargs):
        issue = get_object_or_404(Issue, pk=issue_pk)
        comments = issue.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def create(self, request, project_pk=None, issue_pk=None, *args, **kwargs):
        issue = get_object_or_404(Issue, pk=issue_pk)
        author_user = self.request.user
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author_user=author_user, issue=issue)
        return Response(serializer.data)

    def retrieve(self, request, project_pk=None, issue_pk=None, pk=None, *args, **kwargs):
        comment = get_object_or_404(Comment, issue=issue_pk, pk=pk)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    def destroy(self, request, project_pk=None, pk=None, issue_pk=None, *args, **kwargs):
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
