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
    """
    User can get access only for his personal info.
    Trying to get another user info will be restricted
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if hasattr(obj, 'sender') and hasattr(obj, 'receiver'):
            #  This condition checks permissions to get list of messages
            return bool(obj.sender == request.user or obj.receiver == request.user)
        elif hasattr(obj, 'user'):
            return obj.user.uid == request.user.uid
        elif hasattr(obj, 'sales_department'):
            return obj.sales_department.uid == request.user.uid
        elif obj.__name__ in ('NewsItem', 'Document'):
            return obj.house.sales_department.uid == request.user.uid
        else:
            return False
