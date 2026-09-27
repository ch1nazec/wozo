from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (SellerRegisterView, SellerViewSet,
                    UserViewSet, UserRegisterView,
                    UserProfileView, UserLoginView,
                    AgentViewSet, PersonalDataViewSet)


router = DefaultRouter()

router.register(r'sellers', SellerViewSet, basename='seller')
router.register(r'users', UserViewSet, basename='user')
router.register(r'agents', AgentViewSet, basename='agent')
router.register(r'personals', PersonalDataViewSet, basename='personal')

urlpatterns = \
[
    path('seller/register/', SellerRegisterView.as_view(), name='seller-register'),
    path('register/', UserRegisterView.as_view(), name='user-register'),

    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('login/', UserLoginView.as_view(), name='user-login'),

    path('', include(router.urls)),
]
