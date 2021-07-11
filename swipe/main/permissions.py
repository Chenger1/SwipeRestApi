from rest_framework.permissions import BasePermission


class IsProfileOwner(BasePermission):
    """ Only profile owner can change his own info """
    def has_object_permission(self, request, view, obj):
        return obj.uid == request.user.uid

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'sender') and hasattr(obj, 'receiver'):
            return bool(obj.sender == request.user or obj.receiver == request.user)
        return obj.user.uid == request.user.uid
