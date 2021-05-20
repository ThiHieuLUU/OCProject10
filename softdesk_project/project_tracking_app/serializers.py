from rest_framework import serializers
from .models import (
    Project,
    Contributor,
    Issue,
    Comment,
)

# from django.contrib.auth import get_user_model
# User = get_user_model()

# from softdesk_project.users.serializers import UserSerializer

from softdesk_project.users.models import User


# from django.conf import settings
# User = settings.AUTH_USER_MODEL

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email')


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


class ProjectSerializer(DynamicFieldsModelSerializer):
    # users = UserSerializer(read_only=True, many=True)

    class Meta:
        model = Project
        # fields = ['users', 'title', 'description']
        fields = ['title', 'description']
        # fields = '__all__'


class ContributorSerializer(DynamicFieldsModelSerializer):
    # user = UserSerializer()
    # project = ProjectSerializer()
    class Meta:
        model = Contributor
        fields = '__all__'
        depth = 2


class IssueSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Issue
        fields = '__all__'
        depth = 2


class CommentSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        depth = 2
