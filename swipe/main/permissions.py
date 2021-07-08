from rest_framework.permissions import BasePermission


class IsProfileOwner(BasePermission):
    """ Only profile owner can change his own info """
    def has_object_permission(self, request, view, obj):
        return obj.uid == request.user.uid
