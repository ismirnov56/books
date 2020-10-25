from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrStaffReadOnly(BasePermission):
    """
    Просматривать могут все, но изменять, удалять
    могут только владельцы книги или пользователи с флагом is_staff.
    """

    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_authenticated and
            (obj.owner == request.user or request.user.is_staff)
        )
