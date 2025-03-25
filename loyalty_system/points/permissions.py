from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

class ReadOnlyPermission(permissions.BasePermission):
    """
    Custom permission to only allow read-only access.
    """
    def has_permission(self, request, view):
        # Only allow read-only actions (GET, HEAD, OPTIONS)
        if request.method not in permissions.SAFE_METHODS:
            raise PermissionDenied("You don't have permission to modify points. Points will add to your account everytime you purchase a product.")
        return True
