from django.shortcuts import render, get_object_or_404
from rest_framework import generics, mixins

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.exceptions import NotFound
from rest_framework.decorators import action
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import AllowAny
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
    """
    A viewset for viewing and editing project instances.
    """
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return self.request.user.projects.all() # Only projects of authenticated user

    def list(self, request):
        queryset = self.get_queryset()
        serializer = ProjectSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        # queryset = Project.objects.filter()
        queryset = self.get_queryset()
        project = get_object_or_404(queryset, pk=pk)
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        # many = True if isinstance(request.data, list) else False
        # serializer = ProjectSerializer(data=request.data, many=many)
        serializer = ProjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = request.data
        user = request.user

        new_project = Project.objects.create(
            title=data["title"], description=data['description'], project_type=data["project_type"])

        new_project.save()
        contributor = Contributor.objects.create(project=new_project, user=user, permission="Author")

        # serializer = ProjectSerializer(new_project)
        serializer = ContributorSerializer(contributor) # Display contributor serializer or project?

        return Response(serializer.data)

class UserViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    # ListCreateAPIView
):
    """
    A viewset for viewing and editing issue instances.
    """
    # serializer_class = UserSerializer
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        else:
            return ContributorSerializer

    def list(self, request, project_pk=None):
        project = get_object_or_404(Project, pk=project_pk)
        # project = Project.objects.get(pk=project_pk)
        users = project.users.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def create(self, request, project_pk=None):
        data = request.data
        required_field = "user_choice"
        if required_field in data:
            user_choice = data.get(required_field)
            user_email = user_choice  # This test for email, must to generate
            print(user_email)
            user = get_object_or_404(User, email=user_email)
            project = get_object_or_404(Project, pk=project_pk)
            # print(user)

            contributor = Contributor.objects.create(user=user, project=project)
            # user = User.objects.get(pk=1)
            # contributor.user = user
            # contributor.save()
            serializer = ContributorSerializer(contributor)
            return Response(serializer.data)

        else:
            raise("No corresponding user for this operation")

        # serializer = ContributorSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        #
        # project = get_object_or_404(Project, pk=project_pk)
        # contributor = serializer.create(serializer.data)
        # print(serializer.data)

        # contributor1 = Contributor.objects.get(pk=1)
        # ser1 = ContributorSerializer(contributor1)
        # print(ser1.data)
        # print(request.data)
        # print(request.data.get('user_choice'))

        # serializer = ContributorSerializer(data=request.data)
        # print(serializer.is_valid())
        # print(serializer.data)
        # print(serializer.data.get("user_choice"))

        # serializer = ContributorSerializer()
        # print(serializer)
        # contributor.project = project
        # contributor.save()

        # serializer = ContributorSerializer(contributor)
        # serializer = ProjectSerializer(project)  # Use project or contributor
        #
        # user = User.objects.get(pk=1)
        # serializer = UserSerializer(user)
        # return Response(serializer.data)

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
    # permission_classes = ()
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