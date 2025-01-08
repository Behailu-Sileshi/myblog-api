from rest_framework_nested import routers
from django.urls import path
from . import views

router = routers.DefaultRouter()
router.register('posts', views.PostViewSet, basename='posts')
router.register('authors', views.AuthorViewSet, basename='authors')

urlpatterns = router.urls