from django.shortcuts import render, get_object_or_404
from rest_framework import generics, mixins

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

    def list(self, request,):
        queryset = Project.objects.filter()
        serializer = ProjectSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Project.objects.filter()
        client = get_object_or_404(queryset, pk=pk)
        serializer = ProjectSerializer(client)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        many = True if isinstance(request.data, list) else False
        serializer = ProjectSerializer(data=request.data, many=many)
        serializer.is_valid(raise_exception=True)

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

    # @action(detail=True, methods=['get'])
    # # @action(detail=True, methods=['get', 'post'])
    # def users(self, request, pk=None):
    #     project = get_object_or_404(Project, pk=pk)
    #     users = project.users.all()
    #     serializer = UserSerializer(users, many=True)
    #     return Response(serializer.data)

class UserViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing issue instances.
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def list(self, request, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)
        # project = Project.objects.get(pk=project_pk)
        users = project.users.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, project_pk=None):
        queryset = User.objects.filter(pk=pk, projects=project_pk)
        user = get_object_or_404(queryset, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    # def retrieve(self, request, pk=None, project_pk=None):
    #     project = get_object_or_404(Project, pk=project_pk)
    #
    #     queryset = User.objects.filter(pk=pk, project=project_pk)
    #     user = get_object_or_404(queryset, pk=pk)
    #     serializer = UserSerializer(user)
    #     return Response(serializer.data)


class IssueViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing issue instances.
    """
    serializer_class = IssueSerializer
    queryset = Issue.objects.all()

    # def list(self, request, project_pk=None, maildrop_pk=None):
    #     queryset = Issue.objects.filter(issue__project=project_pk, mail_drop=maildrop_pk)
    #     serializer = MailRecipientSerializer(queryset, many=True)
    #     return Response(serializer.data)
    #
    # def retrieve(self, request, pk=None, client_pk=None, maildrop_pk=None):
    #     queryset = MailRecipient.objects.filter(pk=pk, mail_drop=maildrop_pk, mail_drop__client=client_pk)
    #     maildrop = get_object_or_404(queryset, pk=pk)
    #     serializer = MailRecipientSerializer(maildrop)
    #     return Response(serializer.data)

    def list(self, request, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)
        # project = Project.objects.get(pk=project_pk)
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

        # queryset = Issue.objects.filter(issue=issue_pk)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    #
    # def retrieve(self, request, pk=None, client_pk=None, maildrop_pk=None):
    #     queryset = MailRecipient.objects.filter(pk=pk, mail_drop=maildrop_pk, mail_drop__client=client_pk)
    #     maildrop = get_object_or_404(queryset, pk=pk)
    #     serializer = MailRecipientSerializer(maildrop)
    #     return Response(serializer.data)

    # def list(self, request, project_pk=None, maildrop_pk=None):
    #     queryset = Issue.objects.filter(issue__project=project_pk, mail_drop=maildrop_pk)
    #     serializer = MailRecipientSerializer(queryset, many=True)
    #     return Response(serializer.data)


class ContributorViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing contributor instances.
    """
    permission_classes = ()
    serializer_class = ContributorSerializer
    queryset = Contributor.objects.all()

"""
class ClientViewSet(viewsets.ViewSet):
    serializer_class = ClientSerializer

    def list(self, request,):
        queryset = Client.objects.filter()
        serializer = ClientSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Client.objects.filter()
        client = get_object_or_404(queryset, pk=pk)
        serializer = ClientSerializer(client)
        return Response(serializer.data)

class MailDropViewSet(viewsets.ViewSet):
    serializer_class = MailDropSerializer

    def list(self, request, client_pk=None):
        queryset = MailDrop.objects.filter(client=client_pk)
        serializer = MailDropSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, client_pk=None):
        queryset = MailDrop.objects.filter(pk=pk, client=client_pk)
        maildrop = get_object_or_404(queryset, pk=pk)
        serializer = MailDropSerializer(maildrop)
        return Response(serializer.data)

class MailRecipientViewSet(viewsets.ViewSet):
    serializer_class = MailRecipientSerializer

    def list(self, request, client_pk=None, maildrop_pk=None):
        queryset = MailRecipient.objects.filter(mail_drop__client=client_pk, mail_drop=maildrop_pk)
        serializer = MailRecipientSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None, client_pk=None, maildrop_pk=None):
        queryset = MailRecipient.objects.filter(pk=pk, mail_drop=maildrop_pk, mail_drop__client=client_pk)
        maildrop = get_object_or_404(queryset, pk=pk)
        serializer = MailRecipientSerializer(maildrop)
        return Response(serializer.data)
"""