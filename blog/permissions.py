from django.shortcuts import get_object_or_404
from rest_framework import permissions

from .models import Post, Author


class DenyUpdateExceptMe(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'update' and view.action != 'me':
            return False
        return True
 

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.author == obj.owner


class IsPostOwnerOrReadOnly(permissions.BasePermission):
    def is_owner(self, request, view):
        post_pk = view.kwargs.get('post_pk')
        post = get_object_or_404(Post, pk=post_pk)
        author = Author.objects.filter(user=request.user.id).first()
        return post.owner == author
        

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return self.is_owner(request, view)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return self.is_owner(request, view)

    
    

        

