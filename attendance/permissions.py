from rest_framework import permissions


class IsNotStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (getattr(request.user, 'role', None) == 'admin' or getattr(request.user, 'role', None) != 'teacher')