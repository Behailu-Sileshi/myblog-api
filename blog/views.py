from django.db import transaction
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .filters import PostFilter
from .pagination import DefaultPaginationClass
from .permissions import DenyPostDeleteExceptFollowUnfollow, DenyUpdateExceptMe, IsTheAuthor
from .serializers import AuthorSerializer, CommentSerializer, PostSerializer, SimpleAuthorSerializer
from .models import Author, Comment, Post




class AuthorViewSet(ModelViewSet):
    queryset = Author.objects.select_related('user').prefetch_related('followed_by').all()
    http_method_names = ['get', 'post', 'put', 'delete', 'option', 'head']
    pagination_class = DefaultPaginationClass
    filter_backends = [SearchFilter, OrderingFilter]
    ordering_fields = ['follower_count', 'following_count']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
   

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), DenyPostDeleteExceptFollowUnfollow(), DenyUpdateExceptMe()]

    
    def get_serializer_class(self):
        if self.action == 'follow':
            return SimpleAuthorSerializer
        return AuthorSerializer
    
    @action(detail=False, methods=['GET', 'PUT'])
    def me(self, request):
        author = Author.objects.get(user_id=request.user.id)
        
        if request.method == 'GET':
            serializer = AuthorSerializer(author)
            return Response(serializer.data)
        
        elif request.method == 'PUT':
            serializer = AuthorSerializer(author, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.validated_data)

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated])
    def follow(self, request, pk=None):
        with transaction.atomic():
            author = self.get_object()
            user_author = request.user.author
            if author == user_author:
                return Response({'status': "You can't follow yourself."}, status=status.HTTP_403_FORBIDDEN)
            if not user_author.follows.filter(pk=author.pk).exists():
                user_author.follows.add(author)
                user_author.following_count += 1
                author.follower_count += 1

                user_author.save(update_fields=['following_count'])
                author.save(update_fields=['follower_count'])

                return Response({'status': 'followed'})
            return Response({'status': 'already following'}, status=status.HTTP_409_CONFLICT)

    @action(detail=True, methods=['GET', 'DELETE'], permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk=None):
        with transaction.atomic():
            author = self.get_object()
            user_author = request.user.author
            if user_author.follows.filter(pk=author.pk).exists():
                user_author.follows.remove(author)
                user_author.following_count -= 1
                author.follower_count -= 1

                user_author.save(update_fields=['following_count'])
                author.save(update_fields=['follower_count'])

                return Response({'status': 'unfollowed'})
            return Response({'status': 'not following'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def followers(self, request, pk):
        author = self.get_object()
        paginator = DefaultPaginationClass()
        result_page = paginator.paginate_queryset(author.followed_by.all(), request)
        serializer = SimpleAuthorSerializer(result_page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def followings(self, request, pk):
        author = self.get_object()
        paginator = DefaultPaginationClass()
        result_page = paginator.paginate_queryset(author.follows.all(), request)
        serializer = SimpleAuthorSerializer(result_page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)
        
    
    
class PostViewSet(ModelViewSet):
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering_fields = ['published_date', 'updated_at']
    search_fields = ['title', 'body']
    filterset_class = PostFilter
    
    def get_queryset(self):
        author = Author.objects.filter(user_id=self.request.user.id).first()
        if self.request.method == 'GET':
            return Post.objects.all()
        return Post.objects.filter(owner=author)
    
    
    def get_serializer_context(self):
        return {'user_id': self.request.user.id}
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), IsTheAuthor()]



class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ['created_at']

    def get_queryset(self):
        author = Author.objects.filter(user_id=self.request.user.id).first()
        queryset = Comment.objects\
                                .select_related('owner', 'post', 'parent') \
                                .prefetch_related('replies') \
                                .all()
        if self.action in ['list', 'retrieve']:
            return queryset
        return queryset.filter(owner=author)
    
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated(), IsTheAuthor()]
    
    def get_serializer_context(self):
        return {'post_id': self.kwargs['post_pk'],
                'user_id': self.request.user.id}

    




    
    
    
