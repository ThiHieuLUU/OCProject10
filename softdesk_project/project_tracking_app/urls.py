from django.urls import path, include
from rest_framework_nested import routers
from .views import (
    ProjectViewSet,
    IssueViewSet,
    CommentViewSet,
    ProjectUserViewSet,
)

# See: https://github.com/alanjds/drf-nested-routers

# Generate:/projects/
# Generate:/projects/{project_pk}
router = routers.SimpleRouter()
router.register(r'projects', ProjectViewSet, basename='projects')

# Generate:/projects/{project_pk}/issues/
# Generate:/projects/{project_pk}/issues/{issue_pk}
projects_router = routers.NestedSimpleRouter(router, r'projects', lookup='project')
projects_router.register(r'issues', IssueViewSet, basename='issues')

# Generate:/projects/{project_pk}/issues/{issue_pk}/comments/
# Generate:/projects/{project_pk}/issues/{issue_pk}/comments/{comment_pk}
issues_router = routers.NestedSimpleRouter(projects_router, r'issues', lookup='issue')
issues_router.register(r'comments', CommentViewSet, basename='comments')

# Generate:/projects/{project_pk}/users/
# Generate:/projects/{project_pk}/users/{user_pk}
projects_for_users_router = routers.NestedSimpleRouter(router, r'projects', lookup='project')
projects_for_users_router.register(r'users', ProjectUserViewSet, basename='users')

# e.g of an url: http://127.0.0.1:8000/viewset/projects/3/comments/1/issues/1/
urlpatterns = [
    path('', include(router.urls)),
    path('', include(projects_router.urls)),
    path('', include(issues_router.urls)),
    path('', include(projects_for_users_router.urls)),
]
