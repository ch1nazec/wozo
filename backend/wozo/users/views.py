from django.contrib.auth import get_user_model, login

from rest_framework import viewsets, generics, status

from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework import permissions

from rest_framework_simplejwt.tokens import RefreshToken

from pickups.models import PickupPoint
from pickups.serializer import PickupPointSerializer

from .serializers import (
    UserSerializer, SellerSerializer,
    UserRegisterSerializer, SellerRegistrationSerializer,
    UserLoginSerializer,
    AgentSerializer, AgentSerializerRegistration,
    PersonalDataSerializer,
    PersonalDataRegistrationSerializer)
from .filters import SellerFilters, PersonalDataFilters
from .models import Seller, Agent, PersonalData


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
    filterset_class = SellerFilters

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return Seller.objects.all().select_related('user')
        return Seller.objects.filter(is_active=True).select_related('user')


class AgentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Agent.objects.select_related('personal_data', 'personal_data__user').prefetch_related('pickup_points')
        if self.request.user.is_staff:
            return qs
        return qs.filter(personal_data__user=self.request.user)

    def get_serializer_class(self):
        if self.action in {'create','update','partial_update'}:
            return AgentSerializerRegistration
        return AgentSerializer

    @action(methods=['get'], detail=True, url_path='pickup-points')
    def pickup(self, request: Request, pk: int):
        agent = self.get_object()
        pickups = agent.pickup_points.all()
        if not request.user.is_staff:
            pickups = pickups.filter(is_active=True)

        serializer = PickupPointSerializer(pickups, many=True, context={'request': request})
        return Response(data=serializer, status=status.HTTP_200_OK)


class PersonalDataViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = PersonalDataFilters

    def get_serializer_class(self):
        if self.action in {'create', 'update', 'partial_update'}:
            return PersonalDataRegistrationSerializer
        return PersonalDataSerializer

    def get_queryset(self):
        qs = PersonalData.objects.select_related('user')
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)