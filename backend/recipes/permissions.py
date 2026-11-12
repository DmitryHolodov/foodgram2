from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorAdminOrReadOnly(BasePermission):
    """Записывать может только автор объекта или админ; читать — все."""

    def has_permission(self, request, view):
        # список и детальный просмотр — открыты всем,
        # а POST/PUT/PATCH/DELETE — только авторизованным
        return (request.method in SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.is_staff
