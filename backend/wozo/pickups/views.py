from decimal import Decimal

from django.db.models import F, Sum
from django.shortcuts import get_object_or_404

from rest_framework.request import Request
from rest_framework.response import Response

from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework import viewsets

from rest_framework import status, permissions

from .filters import PickupPointFilters
from .permissions import IsAgent
from .models import PickupPoint, OrderPickupHistory, OrderPickup, PickupFeedback, PickupImage
from .serializer import (PickupPointSerializer, OrderPickupHistorySerializer,
                         OrderPickupSerializer, PickupImageSerializer,
                         PickupFeedbackSerializer)
from services.pagination_classes import HunderResultsSetPagination


# Create your views here.
class PickupPointViewSet(viewsets.ModelViewSet):
    queryset = PickupPoint.objects.all()
    permission_classes = [IsAgent, permissions.IsAdminUser]
    serializer_class = PickupPointSerializer
    filterset_class = PickupPointFilters

    pagination_class = HunderResultsSetPagination

    ordering_fields = ('latitude', 'longitude')


    def create(self, request: Request, *args, **kwargs):
        is_many = isinstance(request.data, list)

        serializer = self.get_serializer(data=request.data, many=is_many)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(['GET'], detail=True)
    def images(self, request: Request, pk: int):
        images = PickupImage.objects.filter(pickup_id=pk)

        serializer = PickupImageSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PickupImageViewSet(viewsets.ModelViewSet):
    queryset = PickupImage.objects.all()
    permission_classes = [IsAgent, permissions.IsAdminUser]
    
    serializer_class = PickupImageSerializer

    def get_queryset(self):
        queryset = PickupFeedback.objects.all()
        pickup_id = self.request.query_params.get('pickup')
        if pickup_id:
            queryset = queryset.filter(pickup_id=pickup_id)
        return queryset


class PickupFeedbackViewSet(viewsets.ModelViewSet):
    queryset = PickupFeedback.objects.all()
    serializer_class = PickupFeedbackSerializer


class OrdersPickupPointAPIView(APIView):
    def get(self, request: Request, pickup_id: int):
        pickup_point = get_object_or_404(PickupPoint, id=pickup_id)

        filter_kwargs = {'pickup': pickup_point}
        status_param = request.query_params.get('status')
        if status_param:
            filter_kwargs['order__status'] = status_param

        order_pickups = (OrderPickup.objects \
                .filter(**filter_kwargs)
        .select_related('pickup', 'order')
        .prefetch_related('order__items'))
         
        total_pickup_sum = (
            OrderPickup.objects
            .filter(**filter_kwargs)
            .values('order')
            .annotate(order_sum=Sum(F('order__items__price') * F('order__items__quantity')))
            .aggregate(total=Sum('order_sum'))['total'] or 0
        )
        
        serializer = OrderPickupSerializer(order_pickups, many=True)
        return Response(
            {
                'total_pickup_sum': total_pickup_sum,
                'orders': serializer.data
            },
            status=status.HTTP_200_OK)