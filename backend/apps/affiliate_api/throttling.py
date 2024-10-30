from rest_framework.throttling import AnonRateThrottle


class AffiliateThrottle(AnonRateThrottle):
    scope = 'affiliate_api'
