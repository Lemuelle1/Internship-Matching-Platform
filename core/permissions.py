"""
core/permissions.py
Custom permission classes for role-based access control.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """Only admin users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMIN'


class IsStudent(BasePermission):
    """Only student users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'STUDENT'


class IsAdminOrReadOnly(BasePermission):
    """
    Admins can do anything.
    Students / public can only read (GET, HEAD, OPTIONS).
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role == 'ADMIN'


class IsOwnerOrAdmin(BasePermission):
    """Object-level: owner or admin can access."""
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'ADMIN':
            return True
        # obj could be Profile or Application — both have a user/student field
        owner = getattr(obj, 'user', None) or getattr(obj, 'student', None)
        return owner == request.user
