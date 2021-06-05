from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
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
    IssueSerializer,
    CommentSerializer,
)
# from .permissions import IsAuthorOrReadPostOnly, IsAuthorOrReadPostOnlyProject, IsAuthorOrReadPostOnlyUser, IssuePermission
from .permissions import IsAuthorOrReadPostOnlyUser, IssuePermission, CommentPermission


class ProjectViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing project instances.
    The permission is determined via get_queryset.
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


class ProjectUserViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
):
    # class ProjectUserViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing issue instances.
    the endpoint kind: /projects/, /projects/{id}/
    get_queryset method and get_object method allow to check permission for GET, DELETE method.
    "POST" method is needed to check permission by class IsAuthorOrReadPostOnlyUser
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthorOrReadPostOnlyUser]

    def get_queryset(self):
        projects = self.request.user.projects.all()
        project_pk = self.kwargs["project_pk"]

        project = get_object_or_404(projects, pk=project_pk)
        users = project.users.all()
        return users

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj

    def create(self, request, project_pk=None, *args, **kwargs):
        users = self.get_queryset()  # Also check nested relationship in url
        data = request.data

        user_data = data.pop('user')
        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, **user_serializer.data)

        project = Project.objects.get(pk=project_pk)

        if user in users:
            raise APIException("This user is already added to the project.")

        permission = data.get("permission")
        if permission == 'AUTHOR':
            raise APIException("Select another permission except AUTHOR.")

        serializer = ContributorSerializer(data=data)  # data has popped user data
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user, project=project)

        return Response(serializer.data)

    def destroy(self, request, project_pk=None, pk=None, *args, **kwargs):
        user = self.get_object()  # Which allows also to call has_object_permission, otherwise it will not be checked.

        projects = user.projects.all()
        project = get_object_or_404(projects, pk=project_pk)

        contributor = get_object_or_404(Contributor, user=user, project=project)
        contributor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IssueViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing issue instances.
    """
    serializer_class = IssueSerializer
    # permission_classes = [IsAuthorOrReadPostOnly]

    permission_classes = [IssuePermission]

    # permission_classes = [IsAuthenticatedOrReadOnly]

    def get_project_object_in_endpoint(self):
        """ Get the project in the endpoint and also define/check the permission of nested relationship"""
        projects = self.request.user.projects.all()
        project_pk = self.kwargs["project_pk"]
        project = get_object_or_404(projects, pk=project_pk)
        return project

    def get_queryset(self):
        # project = self.get_project_object_in_endpoint()
        projects = self.request.user.projects.all()
        project_pk = self.kwargs["project_pk"]
        project = get_object_or_404(projects, pk=project_pk)
        issues = project.issues.all()
        return issues

    def create(self, request, project_pk=None, *args, **kwargs):
        # project = self.get_project_object_in_endpoint()
        project = get_object_or_404(Project, pk=project_pk)
        author_user = self.request.user

        serializer = IssueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(project=project, author_user=author_user)
        return Response(serializer.data)

    def perform_update(self, serializer):
        data = serializer.validated_data

        assignee_user_data = data.pop("assignee_user")
        assignee_user = get_object_or_404(User, **assignee_user_data)
        serializer.save(assignee_user=assignee_user)


class CommentViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing comment instances.
    """
    serializer_class = CommentSerializer
    permission_classes = [CommentPermission]

    # queryset = Comment.objects.all()

    def get_queryset(self):
        projects = self.request.user.projects.all()
        project_pk = self.kwargs["project_pk"]
        project = get_object_or_404(projects, pk=project_pk)

        issues = project.issues
        issue_pk = self.kwargs["issue_pk"]
        issue = get_object_or_404(issues, pk=issue_pk)

        comments = issue.comments.all()
        return comments

    def create(self, request, project_pk=None, issue_pk=None, *args, **kwargs):
        # comments = self.get_queryset()  # all comments of a given issue with pk=issue_pk
        # # issue = comments[0].issue
        issue = get_object_or_404(Issue, pk=issue_pk)

        author_user = self.request.user
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author_user=author_user, issue=issue)
        return Response(serializer.data)
