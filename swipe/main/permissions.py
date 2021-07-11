from rest_framework.permissions import BasePermission


class IsProfileOwner(BasePermission):
    """ Only profile owner can change his own info """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.uid == request.user.uid

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'sender') and hasattr(obj, 'receiver'):
            #  This condition checks permissions to get list of messages
            return bool(obj.sender == request.user or obj.receiver == request.user)
        if request.user.is_staff:
            return True
        return obj.user.uid == request.user.uid
