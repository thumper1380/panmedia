from rest_framework.renderers import JSONRenderer
from functools import wraps
from ipware import get_client_ip
from apps.affiliate_api.exceptions import MissingToken
from apps.settings.models import CRMSettings
from apps.utils.responses import ErrorResponse, PanmediaResponse
from apps.affiliate.models import AffiliateRequestLog, APIToken
from .messages import (
    API_RESPONSE_MISSING_TOKEN_MSG,
    API_RESPONSE_INVALID_TOKEN_MSG,
    API_RESPONSE_IP_ADDRESS_NOT_ALLOWED_MSG,
)
from rest_framework.decorators import throttle_classes
from apps.settings.neutrino import Neutrino as NeutrinoAPI

from apps.affiliate.models import APIToken
from .exceptions import (
    MissingToken,
    InvalidToken,
    TokenDisabled,
    InvalidIPAddress,
)
import jwt
from django.conf import settings


def validate_request(token, ip_address):
    if not token:
        raise MissingToken(API_RESPONSE_MISSING_TOKEN_MSG)
    try:
        token = APIToken.objects.get(token=token)
        token.decode()
    except APIToken.DoesNotExist:
        raise InvalidToken(API_RESPONSE_INVALID_TOKEN_MSG)
    except jwt.exceptions.DecodeError:
        raise InvalidToken(API_RESPONSE_INVALID_TOKEN_MSG)
    if not token.is_enabled:
        raise TokenDisabled(API_RESPONSE_INVALID_TOKEN_MSG)
    if not token.ip_exists(ip_address):
        print(ip_address)
        raise InvalidIPAddress(API_RESPONSE_IP_ADDRESS_NOT_ALLOWED_MSG)
    return token


def affiliate_api(func):
    @wraps(func)
    def _wrapper(self, request, *args, **kwargs):
        query_token = request.GET.get(
            'token', None) if settings.DEBUG else None
        auth_token = request.META.get('HTTP_AUTHORIZATION', None)

        if auth_token:
            token = auth_token

        elif query_token:
            token = 'Bearer ' + query_token

        else:
            return ErrorResponse(message=API_RESPONSE_MISSING_TOKEN_MSG, status_code=PanmediaResponse.HTTP_401_UNAUTHORIZED)

        # Take the token after the bearer
        token = token.split(' ')[1]

        try:
            # Get client IP address
            ip_address, is_routable = get_client_ip(request)
            request.ip_address = ip_address

            valid, country, city, region, latitude, longitude = True, 'IL', 'Ramat Gan', 'TA', '32.068424', '34.824785'

            request.country = country
            request.city = city
            request.region = region
            request.latitude = latitude
            request.longitude = longitude
            request.ip_address = ip_address
            request.user_agent = request.META.get('HTTP_USER_AGENT')

            # Validate token and get request information
            request.token = validate_request(token, ip_address)

            request_method = request.method
            request_input = request.data if request_method in [
                'POST', 'PUT', 'PATCH'] else request.query_params.dict()

            # Get request URL and referrer
            request_url = request.build_absolute_uri(
                request.path_info).split('?')[0]

            request_referrer = request.META.get('HTTP_REFERER')

            # Create request log
            request.request_log = AffiliateRequestLog.objects.create(
                token=request.token,
                request_method=request_method,
                request_url=request_url,
                request_referrer=request_referrer,
                request_input=request_input,
            )

        except (
            MissingToken,
            InvalidToken,
            TokenDisabled,
            InvalidIPAddress,
        ) as e:
            error = e.errors
            return ErrorResponse(error, status_code=PanmediaResponse.HTTP_401_UNAUTHORIZED)

        return func(self, request, *args, **kwargs)

    return _wrapper


def log_request_response(view_func):
    @wraps(view_func)
    def _wrapped_view(instance, request, *args, **kwargs):
        # Log the request before the function
        request_method = request.method
        request_url = request.build_absolute_uri(
            request.path_info).split('?')[0]
        request_referrer = request.META.get('HTTP_REFERER', '')
        request_input = request.query_params.dict(
        ) if request_method == 'GET' else request.data

        request.request_log = AffiliateRequestLog.objects.create(
            token=request.token,
            request_method=request_method,
            request_url=request_url,
            request_referrer=request_referrer,
            request_headers=request.headers,
            request_input=request_input,
        )

        # Execute the view function
        response = view_func(instance, request, *args, **kwargs)

        # Update the request log after the function
        request.request_log.response = JSONRenderer().render(response.data).decode('utf-8')
        request.request_log.code = response.status_code
        request.request_log.lead = request.lead if hasattr(request, 'lead') else None
        request.request_log.save()

        # response['custom'] = 'custom data'

        return response

    return _wrapped_view
