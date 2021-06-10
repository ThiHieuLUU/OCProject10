"""Serializers for model in project tracking app ."""

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
    """Serializer is used for a user."""

    email = serializers.EmailField(required=False,
                                   allow_blank=True)  # To get is_valid = True for unique field (email here)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer is used for a project."""

    users = UserSerializer(read_only=True, many=True)

    class Meta:
        model = Project
        fields = ['id', 'title', 'project_type', 'description', 'users']
        read_only_fields = ['id']

    def create(self, validated_data):
        """Override create method."""

        return Project.objects.create(**validated_data)


class ContributorSerializer(serializers.ModelSerializer):
    """Serializer is used for a contributor."""

    user = UserSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)

    class Meta:
        model = Contributor
        fields = ['project', 'user', 'permission']
        read_on_fields = ['role']

    def create(self, validated_data):
        """Override create method."""

        contributor = Contributor.objects.create(**validated_data)
        return contributor

    def save(self, **kwargs):  # "save" method calls "create" method by adding **kwargs to validated_data
        """Override save method."""

        return super().save(**kwargs)


class IssueSerializer(serializers.ModelSerializer):
    """Serializer is used for an issue."""

    author_user = UserSerializer(read_only=True)
    assignee_user = UserSerializer()
    project = ProjectSerializer(read_only=True)

    class Meta:
        model = Issue
        fields = ['id', 'title', 'description', 'tag', 'priority', 'status', 'assignee_user', 'author_user', 'project']
        read_only_fields = ['id']

    def create(self, validated_data):
        """Override create method."""

        assignee_user_data = validated_data.pop("assignee_user")
        assignee_user = get_object_or_404(User, **assignee_user_data)
        issue = Issue.objects.create(**validated_data, assignee_user=assignee_user)
        return issue

    def save(self, **kwargs):
        """Override save method."""
        # issue = super().save(**self.validated_data, **kwargs)
        issue = super().save(**kwargs)
        return issue


class CommentSerializer(serializers.ModelSerializer):
    """Serializer is used for a comment."""

    author_user = UserSerializer(read_only=True)
    issue = IssueSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'description', 'author_user', 'issue']
        read_only_fields = ['id']
        depth = 1

    def create(self, validated_data):
        """Override create method."""

        comment = Comment.objects.create(**validated_data)
        return comment

    def save(self, **kwargs):
        """Override save method."""

        comment = super().save(**self.validated_data, **kwargs)
        return comment
