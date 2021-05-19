from rest_framework import serializers
from .models import (
    Project,
    Contributor,
    Issue,
    Comment,
)

from ..users.serializers import UserSerializer


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


class ProjectSerializer(serializers.ModelSerializer):
    users = UserSerializer(read_only=True, many=True)

    class Meta:
        model = Project
        fields = '__all__'


class ContributorSerializer(serializers.ModelSerializer):
    # user = UserSerializer()
    # project = ProjectSerializer()
    class Meta:
        model = Contributor
        fields = '__all__'
        depth = 2


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = '__all__'
        depth = 2


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        depth = 2
