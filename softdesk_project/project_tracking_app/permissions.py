from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import User, Project, Contributor, Comment, Issue



class IssuePermission(BasePermission):
    message = 'Editing posts is restricted to the author only.'

    def has_object_permission(self, request, view, obj):
        # Permissions are only allowed to the owner of the device.
        if request.method in SAFE_METHODS or request.method == "POST":
            return True
        return request.user == obj.author_user




#
# class OwnerOrModelPermission(ModelPermissions):
#
#     def __same_user(self, obj, request):
#         from users.models import User
#         return isinstance(obj, User) and obj.id == request.user.id
#
#     def __is_owner(self, obj, request):
#         return hasattr(obj, 'owner') and obj.owner is not None and self.__same_user(obj.owner, request)
#
#     def has_permission(self, request, view):
#         return request.user.is_superuser or ModelPermissions().has_permission(request, view)
#
#     def has_object_permission(self, request, view, obj):
#         return request.user.is_superuser or self.__same_user(obj, request) or self.__is_owner(obj, request) or ModelPermissions().has_object_permission \
#             (request, view, obj)

# def get_object(self):
#     obj = get_object_or_404(self.get_queryset())
#     self.check_object_permissions(self.request, obj)
#     return obj
#
# class ExampleView(APIView):
#     permission_classes = (IsAuthenticated,)
#
#     def get(self, request, format=None):
#         content = {
#             'status': 'request was permitted'
#         }
#         return Response(content)
#
#
# from rest_framework import permissions
#
# class BlacklistPermission(permissions.BasePermission):
#     """
#     Global permission check for blacklisted IPs.
#     """
#
#     def has_permission(self, request, view):
#         ip_addr = request.META['REMOTE_ADDR']
#         blacklisted = Blacklist.objects.filter(ip_addr=ip_addr).exists()
#         return not blacklisted
#
# class IsOwnerOrReadOnly(permissions.BasePermission):
#     """
#     Object-level permission to only allow owners of an object to edit it.
#     Assumes the model instance has an `owner` attribute.
#     """
#
#     def has_object_permission(self, request, view, obj):
#         # Read permissions are allowed to any request,
#         # so we'll always allow GET, HEAD or OPTIONS requests.
#         if request.method in permissions.SAFE_METHODS:
#             return True
#
#         # Instance must have an attribute named `owner`.
#         return obj.owner == request.user

# class ModelNamePermission(permissions.BasePermission):
#     """
#     Custom permission to only allow owners of an object to edit it.
#     """

    # def has_permission(self, request, view):
    #     if request.method in ['GET']:
    #         return request.user.has_perm('view_modelname')
    #     if request.method in ['POST']:
    #         return request.user.has_perm('add_modelname')
    #     if request.method in ['PUT', 'PATCH']:
    #         return request.user.has_perm('change_modelname')
    #     if request.method in ['DELETE']:
    #         return request.user.has_perm('delete_modelname')
    #     return False
    #
    # def has_object_permission(self, request, view, obj):
    #     if request.method in ['GET']:
    #         return request.user.has_perm('view_modelname', obj)
    #     if request.method in ['POST']:
    #         return request.user.has_perm('add_modelname', obj)
    #     if request.method in ['PUT', 'PATCH']:
    #         return request.user.has_perm('change_modelname', obj)
    #     if request.method in ['DELETE']:
    #         return request.user.has_perm('delete_modelname', obj)
    #     return False
