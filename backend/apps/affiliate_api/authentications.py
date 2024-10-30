from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from apps.affiliate.models import APIToken, Affiliate
from ipware import get_client_ip

# Adjust the import path as needed
from .exceptions import MissingToken, InvalidToken, TokenDisabled, InvalidIPAddress
from django.conf import settings

from .messages import (
    API_RESPONSE_MISSING_TOKEN_MSG,
    API_RESPONSE_INVALID_TOKEN_MSG,
    API_RESPONSE_IP_ADDRESS_NOT_ALLOWED_MSG,
)
import jwt


def get_authorization_header(request):
    if settings.DEBUG and request.method == 'GET':
        auth = f'Bearer {request.GET.get("token", "")}'
        return auth.encode()

    auth = request.META.get('HTTP_AUTHORIZATION', b'')
    if isinstance(auth, type('')):
        # Work around django test client oddness
        auth = auth.encode('iso-8859-1')
    return auth


class AffiliateApiAuthentication(BaseAuthentication):
    keyword = 'Bearer'

    def validate_request(self, token, ip_address):
        if not token:
            raise MissingToken(API_RESPONSE_MISSING_TOKEN_MSG)
        try:
            token = APIToken.objects.get(token=token)
            token.decode()
        except APIToken.DoesNotExist:
            raise InvalidToken(API_RESPONSE_INVALID_TOKEN_MSG)
        except jwt.exceptions.DecodeError:
            raise InvalidToken(API_RESPONSE_INVALID_TOKEN_MSG)
        if not token.is_active or not token.affiliate.is_active or not token.affiliate.user.is_active:
            raise TokenDisabled(API_RESPONSE_INVALID_TOKEN_MSG)
        if not token.ip_exists(ip_address):
            print(ip_address)
            raise InvalidIPAddress(API_RESPONSE_IP_ADDRESS_NOT_ALLOWED_MSG)
        return token

    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != self.keyword.lower().encode():
            raise exceptions.AuthenticationFailed(
                API_RESPONSE_MISSING_TOKEN_MSG)

        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)

        elif len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)

        try:

            jwt_token = auth[1].decode()
            # Get client IP address
            ip_address, is_routable = get_client_ip(request)

            # Validate token and get request information
            token = self.validate_request(jwt_token, ip_address)

            request.token = token
            request.affiliate = token.affiliate

            return (token.affiliate.user, token)
            # Return the user associated with the token and the token itself
        except (MissingToken, InvalidToken, TokenDisabled, InvalidIPAddress) as e:
            raise exceptions.AuthenticationFailed(e.errors)

    def authenticate_header(self, request):
        return self.keyword
