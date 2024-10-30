# Django imports
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Third-party imports
from ipware import get_client_ip
from rest_framework import exceptions, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import Throttled
from rest_framework.parsers import JSONParser
from drf_spectacular.utils import extend_schema

# Local application imports
from apps.affiliate.models import Affiliate, APIToken
from apps.affiliate.serializers import (
    ErrorResponseSerializer, LeadResponseSerializer, PixelSerializer
)
from apps.offer.models import Offer
from apps.settings.serializers import create_form_serializer
from apps.trafficdata.models import TrafficData
from .serializers import (
    AffiliateLeadsSerializer, AffiliateSalesSerializer, LeadRequestSerializer, LeadRequestSerializerView
)
from apps.trafficdata.states import StateChoices
from apps.utils.messages import LEAD_NOT_ACCPTED_MESSAGE
from apps.utils.responses import (
    ErrorResponse, PanmediaResponse, SuccessResponse,
    ValidationErrorResponse, ValidationErrorResponseSerializer
)
from .authentications import AffiliateApiAuthentication
from .decorators import log_request_response
from .messages import AFFILIATE_POST_LEAD_DESCRIPTION, AFFILIATE_GET_LEADS_DESCRIPTION, AFFILIATE_GET_SALES_DESCRIPTION
from .mixin import RequestLoggingMixin
from .permissions import IsAffiliate
from .throttling import AffiliateThrottle
from .serializers import create_dynamic_lead_request_serializer

from apps.offer.models import Offer


class AffiliateAPIViewSet(RequestLoggingMixin, viewsets.ViewSet):
    """
    Handles affiliate API actions, including managing leads and sales.
    Includes enhanced exception handling and optimized data processing.
    """
    parser_classes = [JSONParser]
    authentication_classes = [AffiliateApiAuthentication]
    permission_classes = [IsAffiliate]
    throttle_classes = [AffiliateThrottle]

    def get_serializer_class(self):

        if self.action == 'leads':
            form = Offer.objects.get(name='API').lead_form
            DynamicFormSerializer = create_dynamic_lead_request_serializer(
                form)
            return DynamicFormSerializer

    @extend_schema(
        methods=['POST'],
        tags=['Affiliate API'],
        operation_id='push-lead',
        description=AFFILIATE_POST_LEAD_DESCRIPTION,
        summary=_("Push Lead"),
        responses={

            201: LeadResponseSerializer,  # lead created
            400: ValidationErrorResponseSerializer,  # validation error
            401: ErrorResponseSerializer,  # invalid token
            409: ErrorResponseSerializer,  # lead declined
        }
    )
    @extend_schema(
        tags=['Affiliate API'],
        operation_id='get-leads',
        summary=_("Get Leads"),
        description=AFFILIATE_GET_LEADS_DESCRIPTION,
        responses={
            200: AffiliateLeadsSerializer,
            401: ErrorResponseSerializer,
        },
    )
    @log_request_response
    @action(detail=False, methods=['GET', 'POST'], url_path='leads', url_name='leads')
    def leads(self, request, **kwargs):
        """Handles affiliate leads, including fetching and saving them."""
        if request.method == 'GET':
            return self._get_leads(request)
        elif request.method == 'POST':
            return self._post_leads(request)

    @extend_schema(
        tags=['Affiliate API'],
        operation_id='get-sales',
        description=AFFILIATE_GET_SALES_DESCRIPTION,
        summary=_("Get Sales"),
        responses={
            200: AffiliateSalesSerializer,
            401: ErrorResponseSerializer,
        },
        auth=None,
    )
    @log_request_response
    @action(detail=False, methods=['GET'], url_path='sales')
    # @ affiliate_api_decorator
    def sales(self, request, pk=None, **kwargs):
        """Handles affiliate sales, including fetching and serializing them."""
        return self._get_sales(request)

    def _get_leads(self, request):
        """Fetches and serializes affiliate leads."""
        api_token: APIToken = request.token
        affiliate: Affiliate = request.affiliate
        qs = affiliate.trafficdata.filter(
            afm_state__in=[StateChoices.LEAD_PUSHED, StateChoices.SALE]).order_by('-created_at')
        qs = qs.filter(created_at__gte=timezone.now() -
                       timezone.timedelta(days=30))
        serialiser = AffiliateLeadsSerializer(qs, many=True, context={
            'can_see_lead_info': api_token.can_see_lead_info,
            'can_see_real_status': api_token.can_see_real_status,
        })
        return SuccessResponse(data=serialiser.data, status_code=PanmediaResponse.HTTP_200_OK)

    def _post_leads(self, request):
        """Processes and saves new affiliate leads."""

        data = request.data

        form_data = self._get_form_data(request)

        print(data)
        # return Response(form_data)
        affiliate = request.affiliate
        funnel = request.token.offer
        lead_serializer = LeadRequestSerializer(data=data, context={
            'affiliate': affiliate,
            'funnel': funnel,
        })

        try:
            lead_serializer.is_valid(raise_exception=True)

            # validate form data
            form = funnel.lead_form
            form_serializer = create_form_serializer(form)

            serialized_form = form_serializer(data=form_data)
            serialized_form.is_valid(raise_exception=True)

            request.lead = lead_serializer.save()

            request.lead._set_profile(**form_data)

            request.lead.form_complete()
            request.lead.save()

            request.lead.push_brands()

        except Offer.DoesNotExist:
            return ErrorResponse(LEAD_NOT_ACCPTED_MESSAGE, status_code=PanmediaResponse.HTTP_400_BAD_REQUEST)
        except serializers.ValidationError as e:
            return ValidationErrorResponse(e.detail)
        except Exception as e:
            request.lead.error(e)
            return ErrorResponse(LEAD_NOT_ACCPTED_MESSAGE, status_code=PanmediaResponse.HTTP_400_BAD_REQUEST)

        auto_login_url = request.lead.generate_auto_login_url()
        pixels = request.lead.affiliate.get_pixels(goal='lead')
        pixels_serializer = PixelSerializer(pixels, many=True).data

        return SuccessResponse(auto_login_url=auto_login_url, pixels=pixels_serializer, status_code=PanmediaResponse.HTTP_201_CREATED)

    def _get_sales(self, request):
        """Fetches and serializes affiliate sales."""
        affiliate: Affiliate = request.affiliate
        qs = affiliate.sales().order_by('-click_created_at')
        serialiser = AffiliateSalesSerializer(qs, many=True)
        return SuccessResponse(data=serialiser.data, status_code=PanmediaResponse.HTTP_200_OK)

    def _get_form_data(self, request):
        """Extracts form data from the request, removing processed fields."""
        token = request.token
        form_fields = token.offer.lead_form.fields.all()
        form_data = {field.key: request.data.pop(
            field.key, None) for field in form_fields}
        return form_data

    def handle_exception(self, exc):
        if isinstance(exc, Throttled):
            return ErrorResponse(message=exc.detail, status_code=ErrorResponse.ERR_429)

        if isinstance(exc, exceptions.AuthenticationFailed):
            return ErrorResponse(message=exc.detail, status_code=ErrorResponse.ERR_401)

        if isinstance(exc, exceptions.MethodNotAllowed):
            return ErrorResponse(message=exc.detail, status_code=ErrorResponse.ERR_405)

        return super().handle_exception(exc)


def redirect(request):
    r = request.GET.get('r')
    ip_address, is_routable = get_client_ip(request)
    if not r:
        return HttpResponseBadRequest()
    try:
        lead = TrafficData.objects.get_by_jwt_token(r)
    except Exception as e:

        return HttpResponseBadRequest()

    if lead.auto_login.proxy_passed:
        return HttpResponseBadRequest()
    lead.auto_login._pass(ip_address=ip_address)
    return HttpResponseRedirect(lead.auto_login.url)
