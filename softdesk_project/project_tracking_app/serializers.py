from django.shortcuts import get_object_or_404
from django.utils.functional import lazy
from rest_framework import serializers
from .models import (
    Project,
    Contributor,
    Issue,
    Comment,
)

from django.contrib.auth import get_user_model

User = get_user_model()

class DynamicFieldsModelSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email')



class ProjectSerializer(DynamicFieldsModelSerializer):
    users = UserSerializer(read_only=True, many=True) # Display User info for serialisation (Get, retrieve)

    class Meta:
        model = Project
        fields = ['title', 'project_type', 'description', 'users']


class IssueSerializer(serializers.ModelSerializer):
    tag = serializers.ChoiceField(choices=Issue.TAG_CHOICES)
    priority = serializers.ChoiceField(choices=Issue.PRIORITY_CHOICES)  # priority (LOW, MEDIUM or HIGH)
    status = serializers.ChoiceField(choices=Issue.STATUS_CHOICES) # status (To do, In progress or Completed)
    author_user = UserSerializer()
    # Do not put the same related name as which of author_user
    # assignee_user = models.ForeignKey(User, related_name='assignee_issues', on_delete=models.CASCADE)  # Default : author
    assignee_user = UserSerializer()
    project = ProjectSerializer()

    class Meta:
        model = Issue
        fields = '__all__'
        depth = 2


class CommentSerializer(DynamicFieldsModelSerializer):
    author_user = UserSerializer(read_only=True)
    issue = IssueSerializer()
    class Meta:
        model = Comment
        fields = ['description', 'author_user', 'issue']
        # fields = '__all__'
        # depth = 2


def get_users():
    users = User.objects.all()
    # user_choices = ((user.first_name + user.last_name, user.email) for user in users)
    # user_choices = [user.first_name + user.last_name for user in users]
    user_choices = [user.email for user in users]
    return user_choices

# class ContributorSerializer(DynamicFieldsModelSerializer):
#     # user = UserSerializer()
#     # project = ProjectSerializer()
#     class Meta:
#         model = Contributor
#         fields = '__all__'
#         depth = 2


class ContributorSerializer(serializers.ModelSerializer):
    user_choice = serializers.ChoiceField(choices=lazy(get_users, tuple)(), write_only=True)
    # permission = serializers.ChoiceField(choices=Contributor.ROLE_CHOICES)

    class Meta:
        model = Contributor
        # fields = ['permission', 'user_choice']
        fields = ['user_choice']
        read_only_fields = ['project', 'user', 'permission']

    def create(self, validated_data):
        user_choice = validated_data.get("user_choice")  # if none ???
        user_email = user_choice
        print(user_email)
        # user = get_object_or_404(User, email=user_email)
        # user = User.objects.filter(email=user_email)
        # permission = validated_data.get("permission")
        # contributor = Contributor.objects.create(user=user, permission=permission)
        # permission = validated_data.get("permission")
        # contributor = Contributor.objects.create(user=user, permission="Defaut")
        # return contributor

        return Contributor.objects.create()


