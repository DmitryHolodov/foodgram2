from rest_framework.permissions import BasePermission


class MeRequiresAuth(BasePermission):
    """Анониму запрещаем только /users/me/, профили — открыты."""

    def has_permission(self, request, view):
        if getattr(view, 'action', None) == 'me':
            return request.user.is_authenticated
        return True
