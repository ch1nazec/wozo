from django.contrib.auth import get_user_model
from rest_framework import viewsets, generics
from rest_framework import permissions
from .serializers import UserSerializer, SellerSerializer, UserRegisterSerializer, SellerRegistrationSerializer
from .models import Seller


CustomUser = get_user_model()


# Create your views here.
class UserRegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = (permissions.AllowAny,)


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class SellerRegisterView(generics.CreateAPIView):
    queryset = Seller.objects.all()
    serializer_class = SellerRegistrationSerializer
    permission_classes = (permissions.IsAuthenticated,)


class SellerViewSet(viewsets.ModelViewSet):
    serializer_class = SellerSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return Seller.objects.all().select_related('user')
        return Seller.objects.filter(is_active=True).select_related('user')
    