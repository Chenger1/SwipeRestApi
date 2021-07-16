from rest_framework import permissions


class IsProfileOwner(permissions.BasePermission):
    """ Only profile owner can change his own info """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.uid == request.user.uid

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.is_staff:
            return True
        return obj.user == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.is_staff:
            return True
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsMessageSenderOrReceiver(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(obj.sender == request.user or obj.receiver == request.user)
