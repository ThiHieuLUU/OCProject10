from django.urls import path, include
from rest_framework_nested import routers
from .views import (
    ProjectViewSet,
    IssueViewSet,
    CommentViewSet,
    ContributorViewSet,
    ProjectUserViewSet,
)

# See: https://github.com/alanjds/drf-nested-routers

router = routers.SimpleRouter()
router.register(r'projects', ProjectViewSet, basename='projects')
# Generate: /viewset/projects/
# Generate: /viewset/projects/{project_pk}

projects_router = routers.NestedSimpleRouter(router, r'projects', lookup='project')
projects_router.register(r'issues', IssueViewSet, basename='issues')
# Generate: /viewset/projects/{project_pk}/issues/
# Generate: /viewset/projects/{project_pk}/issues/{issue_pk}

issues_router = routers.NestedSimpleRouter(projects_router, r'issues', lookup='issue')
issues_router.register(r'comments', CommentViewSet, basename='comments')
# Generate: /viewset/projects/{project_pk}/issues/{issue_pk}/comments/
# Generate: /viewset/projects/{project_pk}/issues/{issue_pk}/comments/{comment_pk}


router.register(r'contributors', ContributorViewSet, basename='contributors')
# Generate: /viewset/projects/
# Generate: /viewset/projects/{project_pk}

projects_for_users_router = routers.NestedSimpleRouter(router, r'projects', lookup='project')
projects_for_users_router.register(r'users', ProjectUserViewSet, basename='users')

# http://127.0.0.1:8000/viewset/projects/3/comments/1/issues/1/
urlpatterns = [
    path('', include(router.urls)),
    path('', include(projects_router.urls)),
    path('', include(issues_router.urls)),
    path('', include(projects_for_users_router.urls)),

]
