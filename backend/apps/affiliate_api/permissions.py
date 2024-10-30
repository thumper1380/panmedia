from rest_framework import permissions


class IsAffiliate(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the user is authenticated and is an affiliate
        return request.user.is_authenticated and hasattr(request.user, 'affiliate')
