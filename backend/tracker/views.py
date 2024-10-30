from django.db import transaction
from django_fsm import TransitionNotAllowed
from rest_framework.decorators import action
from rest_framework.response import Response

from rest_framework import serializers, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView

from django.shortcuts import redirect
from django.http import HttpResponseBadRequest
from django.http import HttpResponseNotFound
from apps.affiliate.serializers import PixelSerializer
from apps.offer.models import Offer
from apps.settings.exceptions import FormException
from apps.affiliate.models import Affiliate
from apps.traffic_distribution.exceptions import RotationDoesNotExist
from apps.trafficdata.models import TrafficData
from apps.trafficdata.exceptions import InvalidToken
from apps.settings.serializers import FormSerializer
from apps.utils.messages import LEAD_NOT_ACCPTED_MESSAGE
from apps.utils.responses import ErrorResponse, SuccessResponse, ValidationErrorResponse
from .helpers import parse_accept_language
from ipware import get_client_ip
from urllib.parse import urljoin
from user_agents import parse

from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings

from apps.trafficdata.exceptions import PushLeadException

# country serializer
from django_countries.serializer_fields import CountryField
from apps.settings.serializers import create_form_serializer


class DevicesTypes:
    MOBILE, TABLET, DESKTOP, SMART_TV, CONSOLE, OTHER, = 'Mobile', 'Tablet', 'Desktop', 'Smart TV', 'Console', 'Other'


CLICK_ID_PARAMETER_NAME = settings.CLICK_ID_PARAMETER_NAME
REDIRECT_URL_PARAMETER_NAME = settings.REDIRECT_URL_PARAMETER_NAME


class TrackerViewSet(viewsets.ViewSet):

    def __ip_info(self, request):
        # Logic to lookup IP info
        # Example, replace with actual logic
        return True, "FR", "Paris", "Île-de-France", 48.8566, 2.3522

    def __parse_ua(self, request):
        ua = parse(request.META.get('HTTP_USER_AGENT', ''))
        return ua

    def __get_device_type(self, request):
        ua = self.__parse_ua(request)

        if ua.is_pc:
            device_type = DevicesTypes.DESKTOP
        elif ua.is_mobile:
            device_type = DevicesTypes.MOBILE
        elif ua.is_tablet:
            device_type = DevicesTypes.TABLET
        elif 'smart-tv' in str(ua).lower():
            device_type = DevicesTypes.SMART_TV
        elif 'console' in str(ua).lower() or 'playstation' in str(ua).lower() or 'xbox' in str(ua).lower():
            device_type = DevicesTypes.CONSOLE
        else:
            device_type = DevicesTypes.OTHER

        return device_type

    def __get_os_version(self, request):
        # Logic to parse OS version
        ua = self.__parse_ua(request)
        user_agent_platform_version = request.META.get(
            'HTTP_SEC_CH_UA_PLATFORM_VERSION', 0)
        os_version = ua.os.version_string
        if ua.os.family == 'Windows':
            # Detect Windows 11
            platform_version = user_agent_platform_version
            if (user_agent_platform_version):
                platform_version = int(
                    user_agent_platform_version.replace('"', '').split('.')[0])
                if platform_version >= 13:
                    os_version = '11'

        return os_version

    def handle_redirect(self, redirect_type: Offer.RedirectType, redirect_url: str):
        if redirect_type == Offer.RedirectType.HTTP_REDIRECT:
            return HttpResponseRedirect(redirect_url)
        elif redirect_type == Offer.RedirectType.META_REDIRECT:
            return HttpResponse(f'<meta http-equiv="refresh" content="0; url={redirect_url}" />')
        elif redirect_type == Offer.RedirectType.JAVASCRIPT_REDIRECT:
            return HttpResponse(f'<script>window.location.href = "{redirect_url}";</script>')
        elif redirect_type == Offer.RedirectType.REDIRECT_WITHOUT_REFERER:
            response = HttpResponseRedirect(redirect_url)
            response['Referrer-Policy'] = 'no-referrer'
            return response

        return HttpResponseNotFound('Invalid redirect type')

    @action(detail=False, methods=['GET', 'POST'], url_path='track', url_name='track')
    def track(self, request, *args, **kwargs):
        if request.method == 'POST':
            return self.click_landed(request, *args, **kwargs)

        if request.method == 'GET':
            affiliate_id = kwargs.get('affiliate_id')
            alias = kwargs.get('alias')

            print("Got Tracking reqest from ",
                  request.META.get('HTTP_USER_AGENT'))

            if not all([alias, affiliate_id]):
                return HttpResponseBadRequest(f'Missing parameters: {alias} - {affiliate_id}')

            offer = get_object_or_404(Offer, alias=alias)

            # Simplified example, consider encapsulating logic into separate functions or methods
            accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '').split(
                ',')[0] if request.META.get('HTTP_ACCEPT_LANGUAGE', '') else ''
            language = parse_accept_language(accept_language)

            ip_address, is_routable = get_client_ip(request)
            # Assuming self.neutrino.locate(ip_address) is encapsulated elsewhere and handles exceptions
            valid, country, city, region, latitude, longitude = self.__ip_info(
                ip_address)

            if not valid:
                return HttpResponseBadRequest('Invalid IP')

            # Ensure Affiliate exists
            get_object_or_404(Affiliate, id=affiliate_id)

            ua = self.__parse_ua(request)

            device_type = self.__get_device_type(request)

            os_version = self.__get_os_version(request)

            aff_sub_dict = {f'aff_sub_{i}': request.GET.get(
                f'aff_sub_{i}', '') for i in range(1, 21)}

            source_id = request.GET.get('source', '')

            click = TrafficData.objects.create(
                funnel=offer,
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT'),
                referrer=request.META.get('HTTP_REFERER', ''),
                affiliate_id=affiliate_id,
                os=ua.os.family,
                os_version=os_version,
                source_id=source_id,
                browser=ua.browser.family,
                browser_version=ua.browser.version_string,
                device_model=ua.device.model,
                device_type=device_type,
                x_requested_with=request.META.get('HTTP_X_REQUESTED_WITH'),
                country=country,
                city=city,
                region=region,
                language=language,
                bot=ua.is_bot,
                latitude=latitude,
                longitude=longitude,
                **aff_sub_dict
            )
            click.register_impression()
            click.save()

            redirect_url = urljoin(
                offer.url, f'?{CLICK_ID_PARAMETER_NAME}={click.p}')

            response = self.handle_redirect(offer.redirect_type, redirect_url)
            # set cookie
            response.set_cookie(CLICK_ID_PARAMETER_NAME, click.p)

            return response

    def click_landed(self, request, *args, **kwargs):
        try:
            # get click identifier from cookie
            click_identifier_value = request.COOKIES.get(
                CLICK_ID_PARAMETER_NAME)
            trafficdata: TrafficData = TrafficData.objects.get_by_jwt_token(
                click_identifier_value)
        except InvalidToken as e:
            # TODO: remove error details
            return Response(str(e), status=status.HTTP_401_UNAUTHORIZED)

        try:
            trafficdata.impression_registered()
            trafficdata.save()
        except:
            pass

        serialized_form = FormSerializer(trafficdata.funnel.lead_form).data
        country = trafficdata.country
        serialized_country = CountryField().to_representation(country)
        return SuccessResponse(form=serialized_form, country=serialized_country, status_code=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], url_path='push-lead', url_name='push-lead')
    def push_lead(self, request, *args, **kwargs):
        # get p value from cookie
        click_identifier_value = request.COOKIES.get('p', None)
        click: TrafficData = TrafficData.objects.get_by_jwt_token(
            click_identifier_value)
        if not click:
            return Response(status_code=status.HTTP_401_UNAUTHORIZED)

        try:
            form = click.funnel.lead_form

            form_data = request.data

            form_serializer = create_form_serializer(form)

            serialized_form = form_serializer(data=form_data)
            serialized_form.is_valid(raise_exception=True)

            click._set_profile(**form_data)
            click.save()  # opt in the user profile data
            click.form_complete()
            click.save()

            click.push_brands()

        except serializers.ValidationError as e:
            return ValidationErrorResponse(e.detail)

        except (TransitionNotAllowed, PushLeadException) as e:
            # Lead Already Pushed
            click.error(e)
            return ErrorResponse(LEAD_NOT_ACCPTED_MESSAGE, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

        auto_login_url = click.generate_auto_login_url()
        pixels = click.affiliate.get_pixels(goal='lead')
        pixels_serializer = PixelSerializer(pixels, many=True).data

        return SuccessResponse(auto_login_url=auto_login_url, pixels=pixels_serializer, status_code=status.HTTP_201_CREATED)

    @action(detail=False, methods=['GET'], url_path='redirect', url_name='redirect')
    def redirect(self, request, *args, **kwargs):
        redirect_token = request.GET.get(REDIRECT_URL_PARAMETER_NAME)
        ip_address, is_routable = get_client_ip(request)
        if not redirect_token:
            return HttpResponseBadRequest()
        try:
            lead: TrafficData = TrafficData.objects.get_by_jwt_token(
                redirect_token)
        except Exception as e:
            return HttpResponseBadRequest(e)

        if lead.auto_login.proxy_passed:
            return HttpResponseBadRequest()
        lead.auto_login._pass(ip_address=ip_address)
        response = HttpResponseRedirect(lead.auto_login.url)
        response['Referrer-Policy'] = 'no-referrer'
        return response

    # @action(detail=False, methods=['GET'], url_path='ipinfo', url_name='ipinfo')
    # def ipinfo(self, request, *args, **kwargs):
    #     ip_address, is_routable = get_client_ip(request)
    #     valid, country, city, region, latitude, longitude = self.__ip_info(
    #         ip_address)
    #     return Response({
    #         'ip_address': ip_address,
    #         'is_routable': is_routable,
    #         'valid': valid,
    #         'country': country,
    #         'city': city,
    #         'region': region,
    #         'latitude': latitude,
    #         'longitude': longitude
    #     })
