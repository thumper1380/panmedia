from apps.affiliate.models import AffiliateRequestLog


class RequestLoggingMixin:
    def log_request(self):
        request = self.request
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
            request_input=request_input,
        )
