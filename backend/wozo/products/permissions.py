from users.models import Seller

from rest_framework.request import Request
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSellerOrAdmin(BasePermission):
    message = 'Является ли пользователь продавцом'


    def has_permission(self, request: Request, view):
        if request.method in SAFE_METHODS:
            return True

        if not (request.user and request.user.is_authenticated):
            return False

        return bool(request.user.is_staff or Seller.objects.filter(user=request.user).exists())



class IsAdminOrReadUser(BasePermission):
    message = 'Проверка на администратора или же разрешено только смотреть'


    def has_permission(self, request: Request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)