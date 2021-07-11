from django.shortcuts import get_object_or_404

from rest_framework.permissions import BasePermission

from _db.models.user import User


class IsProfileOwner(BasePermission):
    """ Only profile owner can change his own info """
    def has_object_permission(self, request, view, obj):
        return obj.uid == request.user.uid

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user.uid == request.user.uid
