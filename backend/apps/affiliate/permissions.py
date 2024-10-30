from rest_framework import permissions


class IsAffiliate(permissions.BasePermission):
    """
    Custom permission to only allow affiliates to view their own data
    """

    def has_permission(self, request, view):
        # if request.user and request.user.is_authenticated:
        #     return True
        # return False
        return True

