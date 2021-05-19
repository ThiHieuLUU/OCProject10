from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views

from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet

router = DefaultRouter()
router.register('projects', ProjectViewSet, basename="Projects")
urlpatterns = router.urls

app_name = "project_tracking_app"

urlpatterns = [
    path('viewset/', include(router.urls)),
]
