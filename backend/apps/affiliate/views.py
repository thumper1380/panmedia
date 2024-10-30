from apps.users.serializers import UserWriteWOPasswordSerializer
from rest_framework.response import Response
from rest_framework import status
from .models import Affiliate
from rest_framework import viewsets
from functools import wraps

from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect

from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from drf_spectacular.utils import extend_schema

from ipware import get_client_ip


from apps.offer.models import Offer
from apps.settings.models import Event
from apps.trafficdata.models import TrafficData


from apps.affiliate.models import APIToken
from apps.affiliate.serializers import (
    AffiliateCreateSerializer, AffiliateDetailSerializer)
from apps.utils.responses import (
    ErrorResponse, PanmediaResponse, SuccessResponse,
    ValidationErrorResponse, ValidationErrorResponseSerializer
)


# ==================================================================================================
# here will be view set to fetch affiliate list, details, create, update, delete


class AffiliateViewSet(viewsets.ModelViewSet):
    """
    Affiliate Model View Set
    """
    queryset = Affiliate.objects.all().order_by('id')
    serializer_class = AffiliateDetailSerializer
    permission_classes = []

    def retrieve(self, request, *args, **kwargs):

        columns = AffiliateDetailSerializer.get_column_info()

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return SuccessResponse(data=serializer.data, status_code=PanmediaResponse.HTTP_200_OK, columns=columns)

    def list(self, request, *args, **kwargs):
        columns = AffiliateDetailSerializer.get_column_info()
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data, status_code=PanmediaResponse.HTTP_200_OK, columns=columns)

    def create(self, request, *args, **kwargs):
        # Use AffiliateCreateSerializer for creating User and Affiliate
        serializer = AffiliateCreateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            affiliate = serializer.save()
            # You might want to use a different serializer here for the response
            # For example, if you have a serializer that includes user data in the affiliate representation
            response_serializer = AffiliateDetailSerializer(affiliate)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['PUT'], url_path='disable', url_name='disable')
    def disable(self, request, pk=None, **kwargs):
        affiliate: Affiliate = self.get_object()
        affiliate = affiliate.disable()

        return SuccessResponse(data=self.serializer_class(affiliate).data, status_code=PanmediaResponse.HTTP_200_OK)

    @action(detail=True, methods=['PUT'], url_path='enable', url_name='enable')
    def enable(self, request, pk=None, **kwargs):
        affiliate: Affiliate = self.get_object()
        affiliate = affiliate.enable()

        return SuccessResponse(data=self.serializer_class(affiliate).data, status_code=PanmediaResponse.HTTP_200_OK)
