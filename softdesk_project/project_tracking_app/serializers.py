from rest_framework import serializers
from .models import (
    Project,
    Contributor,
    Issue,
    Comment,
)

from django.contrib.auth import get_user_model

User = get_user_model()


# from softdesk_project.users.serializers import UserSerializer

# from softdesk_project.users.models import User


# from django.conf import settings
# User = settings.AUTH_USER_MODEL

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'date_joined')


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


class ContributorSerializer(DynamicFieldsModelSerializer):
    # user = UserSerializer()
    # project = ProjectSerializer()
    class Meta:
        model = Contributor
        fields = '__all__'
        depth = 2


class ProjectSerializer(DynamicFieldsModelSerializer):
    users = UserSerializer(read_only=True, many=True) # Not display User field
    # users = UserSerializer(many=True) # Display "Users" field

    # users = ContributorSerializer(many=True)
    #
    # users = serializers.SlugRelatedField(
    #     many=True,
    #     read_only=True,
    #     slug_field='email'
    # )

    class Meta:
        model = Project
        fields = ['title', 'project_type', 'description', 'users']
        # fields = ['title', 'description']
        # fields = '__all__'
        depth = 1  # All info
        # depth = 2  # All info in UserSerializer


class ContributorSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    project = ProjectSerializer() # Display users will be impacted by the manner user is serialized in project
    permission_display = serializers.CharField(
        source='get_permission_display'
    )

    class Meta:
        model = Contributor
        fields = ['user', 'project', 'permission_display']
        # fields = '__all__'

    def create(self, validated_data) -> Contributor:
        # import ipdb;
        # ipdb.set_trace()
        # create key_date_case
        project = Project.objects.create(**validated_data.get('project'))

        # create icd10
        user = User.objects.create(**validated_data.get('user'))

        # create connection
        contributor = Contributor.objects.create(
            user=user, project=project, permission=validated_data.get('permission'),
            role=validated_data.get('role')
        )
        return contributor


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
