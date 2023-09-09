from rest_framework import permissions


class AdminOrReadOnly(permissions.BasePermission):
    """Изменения доступны при наличии прав администратора."""

    message = 'Отсутствуют права админитсратора!'

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated and (
                    request.user.is_admin or request.user.is_superuser))


class AuthorAdminModerator(permissions.BasePermission):
    """Изменения доступны автору,администратору, модератору."""

    message = 'Недостаточно прав!'

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user == obj.author
            or request.user.is_moderator
            or request.user.is_admin
        )


class SuperUserOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_superuser)
