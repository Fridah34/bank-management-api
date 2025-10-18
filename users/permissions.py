from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permissions(self, request, view):
        return request.user.is_authenticated and requested.user.role == 'admin'
    
class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'staff'
    
class IsAdminOrStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return(
            request.user.is_authenticated and
            (request.user.role == 'admin' or request.user.role == 'staff')
        )