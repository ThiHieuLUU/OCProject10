from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import User, Project, Contributor, Comment, Issue
from rest_framework.exceptions import APIException


class UserRole:
    def is_contributor(self, request, view):
        project_pk = view.kwargs['project_pk']
        project = get_object_or_404(Project, pk=project_pk)
        return request.user in project.users.all()

    def is_author(self, request, view, obj):
        if type(obj) is Project:
            contributor = get_object_or_404(Contributor, user=request.user, project=obj)
            return contributor.permission == "AUTHOR"
        if type(obj) in [Issue, Comment]:
            return request.user == obj.author_user


class EndpointNestedRelation:
    # left to right, e.g.: klass1_name/str_pk1/klass2_name/str_pk2
    # An instance of klass1 has many instances of klass2
    #  Mean that obj1 and obj2 must be existed
    def is_belong_to(self, request, view, klass1=None, str_pk1=None, klass2=None, str_pk2=None, *args, **kwargs):
        pk1 = view.kwargs[str_pk1]
        pk2 = view.kwargs[str_pk2]
        obj1 = get_object_or_404(klass1, pk=pk1)
        obj2 = get_object_or_404(klass2, pk=pk2)
        klass1_name_lower = klass1.__name__.lower()
        attr1_name = klass1_name_lower
        object_type_klass1_from_obj2 = getattr(obj2, attr1_name)
        if not object_type_klass1_from_obj2:
            raise APIException("Endpoint format is not correct.")

        return obj1 == object_type_klass1_from_obj2


class IssuePermission(BasePermission, UserRole):
    message = 'Editing/Deleting issue is restricted to the author only.'

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        if request.method == "POST":
            self.message = f"Only contributor of the project can post an issue."
            return UserRole().is_contributor(request, view)  # super of AuthorPermission is Contributor
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS or request.method == "POST":
            return True
        return UserRole().is_author(request, view, obj)


class CommentPermission(BasePermission, UserRole):
    message = 'Editing/Deleting issue is restricted to the author only.'

    def check_endpoint_for_post_method(self, request, view):
        str_project_pk = "project_pk"
        str_issue_pk = "issue_pk"
        return EndpointNestedRelation().is_belong_to(request, view, klass1=Project, str_pk1=str_project_pk,
                                                     klass2=Issue, str_pk2=str_issue_pk)

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        if request.method == "POST":
            self.message = f"Only contributor of the project can post a comment."
            if not self.check_endpoint_for_post_method(request, view):
                self.message = "Project hasn't this issue."
            if not UserRole().is_contributor(request, view):
                self.message = f"Only contributor of the project can post a comment."
            return self.check_endpoint_for_post_method(request, view) and UserRole().is_contributor(request, view)

        return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS or request.method == "POST":
            return True
        return UserRole().is_author(request, view, obj)


# class IsAuthorOrReadPostOnlyProject(BasePermission):
#     """"This permission controls the endpoint kind: /projects/, /projects/{id}/
#      get_queryset method already checks permission for get, delete, destroy.
#     "POST" method is needed to check permission. """
#     message = 'You have no permission for this request.'
#
#     # def has_object_permission(self, request, view, obj):
#     #     if request.method in SAFE_METHODS or request.method == "POST":
#     #         return True
#     #     # e.g http://127.0.0.1:8000/projects/20/
#     #     contributor = get_object_or_404(Contributor, user=request.user, project=obj)
#     #     return contributor.permission == 'AUTHOR'
#
#     def has_permission(self, request, view):
#         if request.method == "POST":
#             return UserRole().is_contributor(request, view)
#         return True


class IsAuthorOrReadPostOnlyUser(BasePermission):
    """This permission controls the endpoint /projects/{id}/users/ or /projects/{id}/users/{id}.
    get_queryset method already checks permission for get, delete, destroy.
    "POST" method is needed to check permission. """

    message = 'You have no permission for this request.'

    def has_permission(self, request, view):
        if request.method == "POST":
            return UserRole().is_contributor(request, view)
        return True
    #
    # def has_object_permission(self, request, view, obj):
    #     # if request.method in SAFE_METHODS or request.method == "POST":
    #     if request.method in SAFE_METHODS:
    #         return True
    #
    #     # e.g http://127.0.0.1:8000/projects/20/users/1/
    #     project_pk = view.kwargs['project_pk']
    #     project = get_object_or_404(Project, pk=project_pk)
    #
    #     contributor = get_object_or_404(Contributor, user=request.user, project=project)
    #     return contributor.permission == 'AUTHOR'
