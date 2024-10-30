from rest_framework import viewsets, decorators, response
from .models import SaleStatus
from .serializers import SaleStatusSerializer
from apps.utils.serializers import create_related_model_serializer
from apps.affiliate.models import Affiliate
from apps.traffic_distribution.models import Advertiser


class SettingsAPIView(viewsets.GenericViewSet):
    def get_queryset(self):
        return

    @decorators.action(detail=False, methods=['get'], url_path='sale-status')
    def sale_status(self, request):
        sale_status = SaleStatus.objects.all()
        serializer = SaleStatusSerializer(sale_status, many=True)
        return response.Response(serializer.data)

    @decorators.action(detail=False, methods=['get'], url_path='affiliate')
    def affiliate(self, request):
        q = request.query_params.get('query', None)
        affiliate = Affiliate.objects.all()
        if q:
            affiliate = affiliate.filter(company_name__icontains=q)
        serializer = create_related_model_serializer(
            Affiliate, 'company_name')(affiliate, many=True)
        return response.Response(serializer.data)

    @decorators.action(detail=False, methods=['get'], url_path='advertiser')
    def advertiser(self, request):
        advertiser = Advertiser.objects.all()
        serializer = create_related_model_serializer(
            Advertiser)(advertiser, many=True)
        return response.Response(serializer.data)
