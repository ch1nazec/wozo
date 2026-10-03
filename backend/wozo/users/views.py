from django.contrib.auth import get_user_model, login
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from rest_framework import viewsets, generics, status

from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

# from rest_framework_extensions.cache.decorators import cache_response
# from rest_framework_extensions.key_constructor.constructors import DefaultKeyConstructor

from rest_framework.generics import DestroyAPIView
from rest_framework import permissions

from rest_framework_simplejwt.tokens import RefreshToken

from pickups.serializer import PickupPointSerializer

from .serializers import (
    UserSerializer, SellerSerializer,
    UserRegisterSerializer, SellerRegistrationSerializer,
    UserLoginSerializer,
    AgentSerializer, AgentSerializerRegistration,
    PersonalDataSerializer,
    PersonalDataRegistrationSerializer)

from .permissions import IsAgent
from .filters import SellerFilters, PersonalDataFilters
from .models import Seller, Agent, PersonalData
from services.pagination_classes import HunderResultsSetPagination, FiftyResultsSetPagination


CustomUser = get_user_model()


# Create your views here.
class UserProfileView(DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    @method_decorator(cache_page(60 * 60 * 2, key_prefix='user_profile'))
    def get(self, request: Request):
        profile = request.user
        serializer = UserSerializer(profile)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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

    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAdminUser,)

    def list(self, request, *args, **kwargs):
        print("USER:", request.user)
        print("AUTH:", request.auth)
        print("AUTHENTICATORS:", request.authenticators)

        return super().list(request, *args, **kwargs)


class SellerRegisterView(generics.CreateAPIView):
    queryset = Seller.objects.all()
    serializer_class = SellerRegistrationSerializer

    permission_classes = (permissions.IsAuthenticated,)


class SellerViewSet(viewsets.ModelViewSet):
    serializer_class = SellerSerializer
    filterset_class = SellerFilters
    pagination_class = FiftyResultsSetPagination


    def get_permissions(self):
        if self.action in {'list', 'retrieve'}:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            return Seller.objects.all().select_related('user')
        return Seller.objects.filter(is_active=True).select_related('user')

    @method_decorator(cache_page(60 * 60 * 2, key_prefix='seller_list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AgentViewSet(viewsets.ModelViewSet):
    # permission_classes = [IsAgent, permissions.IsAdminUser]
    pagination_class = FiftyResultsSetPagination

    cache_response_ttl = 60 * 30

    def get_permissions(self):
        if self.action in {'create', 'retrieve', 'pickup'}:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]

        return [permission() for permission in permission_classes]

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
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class PersonalDataViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filterset_class = PersonalDataFilters
    pagination_class = FiftyResultsSetPagination


    def get_permissions(self):
        if self.action in {'retrieve', 'create', 'destroy', 'list'}:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAdminUser]

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in {'retrieve', 'create', 'destroy'}:
            return PersonalDataRegistrationSerializer
        return PersonalDataSerializer

    def get_queryset(self):
        qs = PersonalData.objects.select_related('user')
        if not self.request.user or self.request.user.is_anonymous:
            return PersonalData.objects.none()
        
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)