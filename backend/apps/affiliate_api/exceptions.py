from django.core.exceptions import ValidationError


class AffiliateAPIException(Exception):
        def __init__(self, errors, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.errors = errors



class InvalidIPAddress(AffiliateAPIException):
        ...

class IPNotAllowed(AffiliateAPIException):
        ...


class InvalidToken(AffiliateAPIException):
        ...

class MissingToken(AffiliateAPIException):
        ...

class TokenDisabled(AffiliateAPIException):
        ...