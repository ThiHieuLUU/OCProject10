from django.urls import path, include
from rest_framework_nested import routers
from .views import (
    ProjectViewSet,
    IssueViewSet,
    CommentViewSet,
    ContributorViewSet,
)

# See: https://github.com/alanjds/drf-nested-routers

router = routers.SimpleRouter()
router.register(r'projects', ProjectViewSet)
# Generate: /viewset/projects/
# Generate: /viewset/projects/{project_pk}

projects_router = routers.NestedSimpleRouter(router, r'projects', lookup='project')
projects_router.register(r'comments', CommentViewSet, basename='comments')
# Generate: /viewset/projects/{project_pk}/comments/
# Generate: /viewset/projects/{project_pk}/comments/{comment_pk}


comments_router = routers.NestedSimpleRouter(projects_router, r'comments', lookup='comment')
comments_router.register(r'issues', IssueViewSet, basename='issues')
# Generate: /viewset/projects/{project_pk}/comments/issues/
# Generate: /viewset/projects/{project_pk}/comments/{comment_pk}/issues/{issue_pk}


# http://127.0.0.1:8000/viewset/projects/3/comments/1/issues/1/
urlpatterns = [
    path('viewset/', include(router.urls)),
    path('viewset/', include(projects_router.urls)),
    path('viewset/', include(comments_router.urls)),
]
