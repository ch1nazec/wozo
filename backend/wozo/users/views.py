from django.contrib.auth import get_user_model, login

from rest_framework import viewsets, generics
from rest_framework import status

from rest_framework.request import Request
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework import permissions

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer, SellerSerializer, UserRegisterSerializer, SellerRegistrationSerializer, UserLoginSerializer
from .models import Seller


CustomUser = get_user_model()


# Create your views here.
class UserProfileView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request: Request):
        profile = request.user
        serializer = UserSerializer(profile)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegisterSerializer

    permission_classes = (permissions.AllowAny,)


class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        login(request, user)

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'Вы успешно вошли в аккаунт.'
        }, status=status.HTTP_200_OK)
        


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    permission_classes = (permissions.IsAdminUser,)


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
    