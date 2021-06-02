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


class IssueSerializer(serializers.ModelSerializer):
    tag = serializers.ChoiceField(choices=Issue.TAG_CHOICES)
    priority = serializers.ChoiceField(choices=Issue.PRIORITY_CHOICES)  # priority (LOW, MEDIUM or HIGH)
    status = serializers.ChoiceField(choices=Issue.STATUS_CHOICES) # status (To do, In progress or Completed)
    author_user = UserSerializer(read_only=True)
    assignee_user = UserSerializer()
    project = ProjectSerializer(read_only=True)

    class Meta:
        model = Issue
        fields = ['id', 'tag', 'priority', 'status', 'author_user', 'assignee_user', 'project']
        read_only_fields = ['id']


    def create(self, validated_data):
        assignee_user_data = validated_data.pop("assignee_user")
        assignee_user = get_object_or_404(User, **assignee_user_data)
        issue = Issue.objects.create(**validated_data, assignee_user=assignee_user)
        return issue

    def save(self, **kwargs):
        # issue = super().save(**self.validated_data, **kwargs)
        issue = super().save(**kwargs)
        return issue


class CommentSerializer(serializers.ModelSerializer):
    author_user = UserSerializer(read_only=True)
    issue = IssueSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'description', 'author_user', 'issue']
        read_only_fields = ['id']
        depth = 1

    def create(self, validated_data):
        comment = Comment.objects.create(**validated_data)
        return comment

    def save(self, **kwargs):
        comment = super().save(**self.validated_data, **kwargs)
        return comment

class ContributorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)
    class Meta:
        model = Contributor
        fields = ['project', 'user', 'permission']
        read_on_fields = ['role']

    def create(self, validated_data):
        contributor = Contributor.objects.create(**validated_data)
        return contributor

    #  "Save" call "create" by adding **kwargs to validated_data
    def save(self, **kwargs):
        return super().save(**kwargs)




