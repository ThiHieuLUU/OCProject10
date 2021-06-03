from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
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
        users = self.get_queryset()
        data = request.data

        user_data = data.pop('user')
        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid()
        user = get_object_or_404(User, **user_serializer.data)

        project = Project.objects.get(pk=project_pk)

        if user in users:
            raise APIException("This user is already added to the project")

        serializer = ContributorSerializer(data=data)  # data has popped user data
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user, project=project)

        return Response(serializer.data)

    def destroy(self, request, project_pk=None, pk=None, *args, **kwargs):
        users = self.get_queryset()
        user = get_object_or_404(users, pk=pk)

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
    permission_classes = [IssuePermission]
    # permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        projects = self.request.user.projects.all()
        project_pk = self.kwargs["project_pk"]
        project = get_object_or_404(projects, pk=project_pk)

        issues = project.issues.all()
        return issues

    def create(self, request, project_pk=None, *args, **kwargs):
        issues = self.get_queryset()  # issues of a given project with pk=project_pk
        project = issues[0].project
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
    queryset = Comment.objects.all()

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
        comments = self.get_queryset()  # all comments of a given issue with pk=issue_pk
        issue = comments[0].issue

        author_user = self.request.user
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author_user=author_user, issue=issue)
        return Response(serializer.data)

