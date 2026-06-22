from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    """
    Object-level permission:
      - Read (GET/HEAD/OPTIONS) allowed for everyone.
      - Write (POST/PUT/PATCH/DELETE) allowed only to the object's author.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        # Support both `author` and `user` field names
        owner = getattr(obj, "author", None) or getattr(obj, "user", None)
        return owner == request.user


class IsAdminOrReadOnly(BasePermission):
    """
    Allows read access to anyone; write access only to admin/staff users.
    Used for Category and Tag management.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
