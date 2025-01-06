from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated

from blog.permissions import IsTheAuthor
from .serializers import PostSerializer
from .models import Author, Post

class PostViewSet(ModelViewSet):
    serializer_class = PostSerializer
    
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
        return [IsTheAuthor()]
    
    
    
