from email.mime import base
from rest_framework_nested import routers
from django.urls import path
from . import views

router = routers.DefaultRouter()
router.register('authors', views.AuthorViewSet, basename='authors')
router.register('posts', views.PostViewSet, basename='posts')

post_router = routers.NestedDefaultRouter(router, 'posts', lookup='post')
post_router.register('comments', views.CommentViewSet, basename='post-comment')
post_router.register('images', views.PostImageViewSet, basename='post-image')
post_router.register('videos', views.PostVideoViewSet, basename='post-video')




urlpatterns = [
    path('follow/<int:pk>/', views.FollowViewSet.as_view({'post': 'follow'}), name='follow'),
    path('unfollow/<int:pk>/', views.FollowViewSet.as_view({'delete': 'unfollow'}), name='unfollow'),
    path('followers/', views.FollowViewSet.as_view({'get': 'followers'}), name='followers'),
    path('followings/', views.FollowViewSet.as_view({'get': 'followings'}), name='followings'),
    ] + router.urls + post_router.urls 