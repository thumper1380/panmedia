from django.http import HttpResponse, Http404, HttpResponsePermanentRedirect
from apps.settings.models import Domain, CRMSettings
from django.conf import settings
# import reverse
from django.urls import reverse, resolve
from django.urls import clear_url_caches, set_urlconf

class DomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # host_domain = request.get_host().split(':')[0]
        # tracking_domains = Domain.objects.filter(type=Domain.DomainType.TRACKING)
        # if host_domain in [d.domain for d in tracking_domains]: # if host domain is tracking domain
        #     url_conf = 'config.tracking_urls'
        # else:
        #     url_conf = 'config.urls'

        # set_urlconf(url_conf)
        response = self.get_response(request)
        response['Accept-CH'] = 'Sec-CH-UA-Platform-Version'
        response['Critical-CH'] = 'Sec-CH-UA-Platform-Version'
        return response