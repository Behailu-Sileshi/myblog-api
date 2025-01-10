from rest_framework_nested import routers
from django.urls import path
from . import views

router = routers.DefaultRouter()
router.register('authors', views.AuthorViewSet, basename='authors')
router.register('posts', views.PostViewSet, basename='posts')


post_router = routers.NestedDefaultRouter(router, 'posts', lookup='post')
post_router.register('comments', views.CommentViewSet, basename='post-comment')
urlpatterns = [
    path('follow/<int:pk>/', views.FollowViewSet.as_view({'post': 'follow'}), name='follow'),
    path('unfollow/<int:pk>/', views.FollowViewSet.as_view({'delete': 'unfollow'}), name='unfollow'),
    

] + router.urls + post_router.urls