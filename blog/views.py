from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import Count
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ViewSet
from django_filters.rest_framework import DjangoFilterBackend

from .filters import PostFilter
from .pagination import DefaultPaginationClass
from .permissions import DenyUpdateExceptMe, IsOwner, IsPostOwnerOrReadOnly
from .serializers import AuthorSerializer, CommentSerializer, PostImageSerializer, PostSerializer, PostVideoSerializer, SimpleAuthorSerializer
from .models import Author, Comment, Post, PostImage, PostVideo





class AuthorViewSet(ModelViewSet):
    queryset = Author.objects.select_related('user').prefetch_related('followed_by').all()
    serializer_class = AuthorSerializer
    http_method_names = ['get', 'put', 'option', 'head']
    pagination_class = DefaultPaginationClass
    filter_backends = [SearchFilter, OrderingFilter]
    ordering_fields = ['follower_count', 'following_count']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
   
   

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), DenyUpdateExceptMe()]

    
    @action(detail=False, methods=['GET', 'PUT'])
    def me(self, request):
        author = request.user.author

        if request.method == 'GET':
            serializer = AuthorSerializer(author)
            return Response(serializer.data)
        
        elif request.method == 'PUT':
            serializer = AuthorSerializer(author, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
    
    
   
    
class PostViewSet(ModelViewSet):
    queryset = Post.objects.annotate(
                    comments_count=Count('comments'),
                    images_count=Count('images'),
                    videos_count=Count('videos'))
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering_fields = ['published_date', 'updated_at']
    search_fields = ['title', 'body']
    filterset_class = PostFilter
    
   
    
    
    def get_serializer_context(self):
        return {'user_id': self.request.user.id}
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), IsOwner()]



class CommentViewSet(ModelViewSet):
    queryset = Comment.objects\
                        .select_related('owner', 'post', 'parent') \
                        .prefetch_related('replies').all()
    serializer_class = CommentSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ['created_at']
    
        
    
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated(), IsOwner()]
    
    def get_serializer_context(self):
        return {'post_id': self.kwargs['post_pk'],
                'user_id': self.request.user.id}


class FollowViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'], url_path='follows', permission_classes=[IsAuthenticated])
    def follow(self, request, pk=None):
        with transaction.atomic():
            author_to_follow = get_object_or_404(Author, pk=pk)
            user_author = request.user.author  # assuming `request.user` has a related `author` object

            if author_to_follow == user_author:
                return Response({'status': "You can't follow yourself."}, status=status.HTTP_403_FORBIDDEN)

            if not user_author.follows.filter(pk=author_to_follow.pk).exists():
                user_author.follows.add(author_to_follow)
                user_author.following_count += 1
                author_to_follow.follower_count += 1

                user_author.save(update_fields=['following_count'])
                author_to_follow.save(update_fields=['follower_count'])

                return Response({'status': 'followed'}, status=status.HTTP_201_CREATED)

            return Response({'status': 'already following'}, status=status.HTTP_409_CONFLICT)

    @action(detail=True, methods=['delete'], url_path='unfollow', permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk=None):
        with transaction.atomic():
            author_to_unfollow = get_object_or_404(Author, pk=pk)
            user_author = request.user.author

            if user_author.follows.filter(pk=author_to_unfollow.pk).exists():
                user_author.follows.remove(author_to_unfollow)
                user_author.following_count -= 1
                author_to_unfollow.follower_count -= 1

                user_author.save(update_fields=['following_count'])
                author_to_unfollow.save(update_fields=['follower_count'])

                return Response({'status': 'unfollowed'}, status=status.HTTP_200_OK)

            return Response({'status': 'not following'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def followers(self, request):
        author = Author.objects.get(user=request.user)
        paginator = DefaultPaginationClass()
        result_page = paginator.paginate_queryset(author.followed_by.all(), request)
        serializer = SimpleAuthorSerializer(result_page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def followings(self, request):
        author = Author.objects.get(user=request.user)
        paginator = DefaultPaginationClass()
        result_page = paginator.paginate_queryset(author.follows.all(), request)
        serializer = SimpleAuthorSerializer(result_page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


class PostImageViewSet(ModelViewSet):
    serializer_class = PostImageSerializer
    permission_classes = [IsPostOwnerOrReadOnly]
    
    def get_queryset(self):
        return PostImage.objects.filter(post_id=self.kwargs.get('post_pk'))
    
    def get_serializer_context(self):
        return {'post_id': self.kwargs.get('post_pk')}
    
            
    
    
class PostVideoViewSet(ModelViewSet):
    serializer_class = PostVideoSerializer
    permission_classes = [IsPostOwnerOrReadOnly]
    
    def get_queryset(self):
        return PostVideo.objects.filter(post_id=self.kwargs.get('post_pk'))
    
    def get_serializer_context(self):
        return {'post_id': self.kwargs.get('post_pk')}

    
    
