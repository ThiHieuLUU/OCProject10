"""Permission to control actions of users:
- Only contributors of a project can access to this project and do some actions:
+ read all/detail of issues/a issue, comments/a comment associated with this project.
+ add a new contributor, issue, comment for the project
- Only author role of an entity (project, issue, comment) can update and delete this entity.
"""

from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import User, Project, Contributor, Comment, Issue
from rest_framework.exceptions import APIException


class UserRole:
    """Class to determine if a user is a contributor (here: author, manager or creator) or an author of a project. """

    def is_contributor(self, request, view):
        """Verify if a user is a contributor of a given project determined from an endpoint."""

        project_pk = view.kwargs['project_pk']
        project = get_object_or_404(Project, pk=project_pk)
        return request.user in project.users.all()

    def is_author(self, request, view, obj):
        """Verify if a user is an author of a given project determined from an endpoint."""

        if type(obj) is Project:
            contributor = get_object_or_404(Contributor, user=request.user, project=obj)
            return contributor.permission == "AUTHOR"
        if type(obj) in [Issue, Comment]:
            return request.user == obj.author_user


class EndpointNestedRelation:
    """Class to verify nested relationship in an endpoint (for any two levels).
    For example:
    From left to right, an endpoint contains: klass1_names/str_pk1/klass2_names/str_pk2
    Where:
    - An instance of klass1 has many instances of klass2
    - An instance of klass2 contains an instance of klass1
    (one to many relation)
    This class serves to verify if the endpoint has a sense in respecting the above nested relationship.
    """

    def is_belong_to(self, request, view, klass1=None, str_pk1=None, klass2=None, str_pk2=None, *args, **kwargs):
        """Verify if an object of klass2 belongs to an object of klass1 determined via an endpoint."""

        pk1 = view.kwargs[str_pk1]
        pk2 = view.kwargs[str_pk2]
        obj1 = get_object_or_404(klass1, pk=pk1)
        obj2 = get_object_or_404(klass2, pk=pk2)
        klass1_name_lower = klass1.__name__.lower()
        attr1_name = klass1_name_lower
        object_type_klass1_from_obj2 = getattr(obj2, attr1_name)
        if not object_type_klass1_from_obj2:
            raise APIException("Nested relationship in the endpoint is not correct.")

        return obj1 == object_type_klass1_from_obj2


class IsAuthorOrReadPostOnlyUser(BasePermission):
    """This permission controls the type of endpoints: /projects/{id}/users/ or /projects/{id}/users/{id}.
    get_queryset method already checks permission for GET/DELETE methods.
    "POST" method is needed to check permission here. """

    message = 'You have no permission for this request.'

    def has_permission(self, request, view):
        """Override has_permission method to treat the POST method."""

        if request.method == "POST":
            return UserRole().is_contributor(request, view)
        return True


class IssuePermission(BasePermission, UserRole):
    """This permission controls the type of endpoints: /projects/{id}/issues/ or /projects/{id}/issues/{id}.

    - get_queryset method already checks permission for GET method.
    - "POST" method is needed to check permission for the nested relationship in the endpoint.
    - PUT/DELETE methods are needed to check permission because only author of an issue can do these actions.
    """

    message = 'Editing/Deleting issue is restricted to the author only.'

    def has_permission(self, request, view):
        """
        Override has_permission method to treat the POST method.
        Return `True` if permission is granted, `False` otherwise.
        """
        if request.method == "POST":
            self.message = "Only contributor of the project can post an issue."
            return UserRole().is_contributor(request, view)
        return True

    def has_object_permission(self, request, view, obj):
        """
        Override has_object_permission method to treat PUT (for update) and DELETE methods.
        Return `True` if permission is granted, `False` otherwise.
        """
        if request.method in SAFE_METHODS:
            return True
        return UserRole().is_author(request, view, obj)


class CommentPermission(BasePermission, UserRole):
    """This permission controls the type of endpoints: /projects/{id}/issues/{id}/comments
     or /projects/{id}/issues/{id}/comments/{id}.

    - get_queryset method already checks permission for GET method.
    - "POST" method is needed to check permission for the nested relationship in the endpoint.
    - PUT/DELETE methods are needed to check permission because only author of a comment can do these actions.
     """

    message = 'Editing/Deleting issue is restricted to the author only.'

    def check_endpoint_for_post_method(self, request, view):
        """Check nested relationship in the endpoint."""

        str_project_pk = "project_pk"
        str_issue_pk = "issue_pk"
        return EndpointNestedRelation().is_belong_to(request, view, klass1=Project, str_pk1=str_project_pk,
                                                     klass2=Issue, str_pk2=str_issue_pk)

    def has_permission(self, request, view):
        """
        Override has_permission method to treat the POST method.
        Return `True` if permission is granted, `False` otherwise.
        """

        if request.method == "POST":
            if not self.check_endpoint_for_post_method(request, view):
                self.message = "Project hasn't this issue."
            if not UserRole().is_contributor(request, view):
                self.message = "Only contributor of the project can post a comment."
            return self.check_endpoint_for_post_method(request, view) and UserRole().is_contributor(request, view)

        return True

    def has_object_permission(self, request, view, obj):
        """
        Override has_object_permission method to treat PUT (for update) and DELETE methods.
        Return `True` if permission is granted, `False` otherwise.
        """

        if request.method in SAFE_METHODS:
            return True
        return UserRole().is_author(request, view, obj)
