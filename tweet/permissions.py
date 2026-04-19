"""
Custom DRF permission classes for tweet operations.

Implements granular permission control:
- Public reads (anyone can view)
- Authenticated writes (only logged-in users can create)
- Owner-only modifications (only tweet owner can edit/delete)
"""

from rest_framework import permissions


class IsPublicReadOnlyOrAuthenticated(permissions.BasePermission):
    """
    Permission class that allows:
    - Public READ-ONLY access for unauthenticated users
    - Full access for authenticated users to their own objects
    - WRITE operations only for authenticated users
    """

    def has_permission(self, request, view):
        # Allow GET, HEAD, OPTIONS for anyone (public read)
        if request.method in permissions.SAFE_METHODS:
            return True

        # For any write operation (POST, PUT, PATCH, DELETE),
        # user must be authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Allow read for everyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # For write operations, only owner can modify
        return obj.user == request.user


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission class that allows:
    - READ access to anyone
    - WRITE/DELETE access only to the object owner
    
    Used for nested resources or when you want to ensure
    ownership checks at the object level.
    """

    def has_object_permission(self, request, view, obj):
        # Allow read-only requests
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object
        return obj.user == request.user
