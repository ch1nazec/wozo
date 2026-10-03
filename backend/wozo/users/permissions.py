from rest_framework.permissions import BasePermission
from rest_framework.request import Request


class IsAgent(BasePermission):
    def has_permission(self, request: Request, view):
        return request.user and request.user.is_authenticated

    
    def has_object_permission(self, request: Request, view, obj):
        return obj.personaldata_agent.user == request.user