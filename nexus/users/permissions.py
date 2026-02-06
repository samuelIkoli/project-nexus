from rest_framework import permissions


class IsTeacher(permissions.BasePermission):
    """
    Allows access only to users with the TEACHER role.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "TEACHER")


class IsLearner(permissions.BasePermission):
    """
    Allows access only to users with the LEARNER role.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "LEARNER")


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` or `teacher` attribute.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        owner = getattr(obj, "owner", None) or getattr(obj, "teacher", None)
        return owner == request.user
