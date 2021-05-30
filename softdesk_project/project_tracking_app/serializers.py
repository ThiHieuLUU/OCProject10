from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import (
    Project,
    Contributor,
    Issue,
    Comment,
)

from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False, allow_blank=True)  # To get is_valid = True for unique field (email here)
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class ProjectSerializer(serializers.ModelSerializer):
    users = UserSerializer(read_only=True, many=True) # Display User info for serialisation (Get, retrieve)

    class Meta:
        model = Project
        fields = ['id', 'title', 'project_type', 'description', 'users']
        read_only_fields = ['id']

    def create(self, validated_data):
        return Project.objects.create(**validated_data)

    def save(self, user=None, permission=None):
        # project = self.create(self.validated_data)
        # contributor = Contributor.objects.create(project=project, user=user, permission=permission)
        contributor = super().save(**self.validated_data, user=user, permission=permission)
        return contributor



class IssueSerializer(serializers.ModelSerializer):
    tag = serializers.ChoiceField(choices=Issue.TAG_CHOICES)
    priority = serializers.ChoiceField(choices=Issue.PRIORITY_CHOICES)  # priority (LOW, MEDIUM or HIGH)
    status = serializers.ChoiceField(choices=Issue.STATUS_CHOICES) # status (To do, In progress or Completed)
    author_user = UserSerializer()
    # assignee_user = models.ForeignKey(User, related_name='assignee_issues', on_delete=models.CASCADE)  # Default : author
    assignee_user = UserSerializer()
    project = ProjectSerializer(read_only=True)

    class Meta:
        model = Issue
        fields = '__all__'
        # depth = 2

    def create(self, validated_data):
        author_user_data = validated_data.pop("author_user")
        author_user = get_object_or_404(User, **author_user_data)
        assignee_user_data = validated_data.pop("assignee_user")
        assignee_user = get_object_or_404(User, **assignee_user_data)
        issue = Issue.objects.create(**validated_data, author_user=author_user, assignee_user=assignee_user)
        return issue

    # def update(self, request, *args, **kwargs):
    #     data = request.data
    #
    #     author_user_data = data.pop("author_user")
    #     author_user = get_object_or_404(User, **author_user_data)
    #
    #     assignee_user_data = data.pop("assignee_user")
    #     assignee_user = get_object_or_404(User, **assignee_user_data)
    #
    #     project = kwargs["instance"].project
    #     super().update(request, project=project, *args, **kwargs)

    # def save(self, project=None):
    #     issue = super().save(**self.validated_data, project=project)
    #     return issue

    def save(self, **kwargs):
        author_user = kwargs["author_user"]

        assignee_user = kwargs["assignee_user"]
        project = kwargs["project"]
        issue = super().save(**self.validated_data, project=project, author_user=author_user, assignee_user=assignee_user)
        return issue


class CommentSerializer(serializers.ModelSerializer):
    author_user = UserSerializer(read_only=True)
    issue = IssueSerializer()
    class Meta:
        model = Comment
        fields = ['description', 'author_user', 'issue']
        # fields = '__all__'
        # depth = 2


class ContributorSerializer(serializers.ModelSerializer):
    # users = UserSerializer(many=True)
    user = UserSerializer()
    class Meta:
        model = Contributor
        fields = ['project', 'user', 'permission']
        read_on_fields = ['project', 'role']
        # fields = '__all__'
        # depth = 2

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = get_object_or_404(User, **user_data)
        contributor = Contributor.objects.create(**validated_data, user=user)
        return contributor




