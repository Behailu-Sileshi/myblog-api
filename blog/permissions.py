from rest_framework import permissions


class IsTheAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner.user_id == request.user.id



class DenyUpdateExceptMe(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'update' and view.action != 'me':
            return False
        return True


class DenyPostDeleteExceptFollowUnfollow(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ['POST', 'DELETE']:
            if view.action not in ['follow', 'unfollow']:
                return False
        return True


