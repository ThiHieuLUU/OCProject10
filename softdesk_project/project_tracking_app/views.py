"""API Views for different requests about user, project, issue and comment.
"""

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response


from .models import (
    User,
    Project,
    Contributor,
    Issue,
)
from .serializers import (
    UserSerializer,
    ProjectSerializer,
    ContributorSerializer,
    IssueSerializer,
    CommentSerializer,
)
from .permissions import (
    IsAuthorOrReadPostOnlyProject,
    IsAuthorOrReadPostOnlyUser,
    IssuePermission,
    CommentPermission,
)

from .exceptions import UniqueConstraint


class ProjectViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing project instances.
    - The type of endpoints: /projects/ or /projects/{id}
    - "GET", "POST" request's permission are satisfied via get_queryset method.
    - "DELETE", "PUT" requests are needed to check author project permission.
    """
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthorOrReadPostOnlyProject]

    def get_queryset(self):
        """Define a set of projects to which the authenticated user can access."""

        return self.request.user.projects.all()  # Only projects of which the authenticated user is contributor.

    def create(self, request, *args, **kwargs):
        """The authenticated user creates a new project."""

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
    """
    A viewset for viewing, adding and deleting a contributor for a given project.
    - The type of endpoints: /projects/{id}/users or /projects/{id}/users/{id}
    - get_queryset method and get_object method allow to check permission for GET request.
    - "POST" request is needed to check permission.
    - "DELETE" request is needed to check author project permission.
    - "PUT" request is not allowed here (can't modify user's information).
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthorOrReadPostOnlyUser]

    def get_queryset(self):
        """Define a set of users associated with a project determined via an endpoint."""

        projects = self.request.user.projects.all()
        project_pk = self.kwargs["project_pk"]

        project = get_object_or_404(projects, pk=project_pk)
        users = project.users.all()
        return users

    def get_object(self):
        """Get a contributor via its id and check permission that authenticated user can do with this contributor."""

        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj

    def create(self, request, project_pk=None, *args, **kwargs):
        """The authenticated user adds a new contributor to a project."""

        users = self.get_queryset()  # Also check nested relationship in url
        data = request.data

        user_data = data.pop('user')
        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, **user_serializer.data)

        project = Project.objects.get(pk=project_pk)

        if user in users:
            raise UniqueConstraint(detail="This user is already one of contributors of the project")

        permission = data.get("permission")
        if permission == 'AUTHOR':
            raise UniqueConstraint(detail="AUTHOR permission existed. Select another permission except AUTHOR.")

        serializer = ContributorSerializer(data=data)  # data has popped user data
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user, project=project)

        return Response(serializer.data)

    def destroy(self, request, project_pk=None, pk=None, *args, **kwargs):
        """The authenticated user deletes a user associated with a project (delete a contributor)."""

        user = self.get_object()  # This also allows to call has_object_permission, otherwise it will not be checked.

        projects = user.projects.all()
        project = get_object_or_404(projects, pk=project_pk)

        contributor = get_object_or_404(Contributor, user=user, project=project)
        contributor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IssueViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing issue instances.
    - The type of endpoints: /projects/{id}/issues or /projects/{id}/issues/{id}
    - get_queryset method and get_object method allow to check permission for GET, DELETE request.
    - "POST" method is needed to check permission.
    - "PUT" and 'DELETE' methods are needed to check author permission for an issue.
    """
    serializer_class = IssueSerializer
    permission_classes = [IssuePermission]

    def get_queryset(self):
        """Define a set of issues associated with a project determined via an endpoint."""

        projects = self.request.user.projects.all()
        project_pk = self.kwargs["project_pk"]
        project = get_object_or_404(projects, pk=project_pk)
        issues = project.issues.all()
        return issues

    def create(self, request, project_pk=None, *args, **kwargs):
        """The authenticated user adds a new issue to a project."""

        project = get_object_or_404(Project, pk=project_pk)
        author_user = self.request.user

        serializer = IssueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(project=project, author_user=author_user)
        return Response(serializer.data)

    def perform_update(self, serializer):
        """The authenticated user updates an issue (permission: the user is also author of the issue)."""

        data = serializer.validated_data

        assignee_user_data = data.pop("assignee_user")
        assignee_user = get_object_or_404(User, **assignee_user_data)
        serializer.save(assignee_user=assignee_user)


class CommentViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing comment instances.
    - The type of endpoints: /projects/{id}/issues/comments/ or /projects/{id}/issues/{id}/comments/{id}
    - get_queryset method and get_object method allow to check permission for GET, DELETE request.
    - "POST" request is needed to check permission.
    - "PUT" and 'DELETE' request are needed to check author permission for a comment.
    """

    serializer_class = CommentSerializer
    permission_classes = [CommentPermission]

    def get_queryset(self):
        """Define a set of comments associated with an issue determined via an endpoint."""

        projects = self.request.user.projects.all()
        project_pk = self.kwargs["project_pk"]
        project = get_object_or_404(projects, pk=project_pk)

        issues = project.issues
        issue_pk = self.kwargs["issue_pk"]
        issue = get_object_or_404(issues, pk=issue_pk)

        comments = issue.comments.all()
        return comments

    def create(self, request, project_pk=None, issue_pk=None, *args, **kwargs):
        """The authenticated user adds a new comment to an issue."""

        issue = get_object_or_404(Issue, pk=issue_pk)
        author_user = self.request.user
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author_user=author_user, issue=issue)
        return Response(serializer.data)
