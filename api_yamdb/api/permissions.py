from rest_framework import permissions


class AdminOrReadOnly(permissions.BasePermission):
    """Изменения доступны при наличии прав администратора."""

    message = 'Отсутствуют права админитсратора!'

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.user == request.user.is_authenticated
                and request.user.is_staff)
