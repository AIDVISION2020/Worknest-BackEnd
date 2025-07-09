# permissions.py

from rest_framework import permissions


class IsWorker(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'worker_profile')


class IsUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return not hasattr(request.user, 'worker_profile')  # assuming only workers have worker_profile
