
import requests
from django.conf import settings

class Neutrino:
    class NeutrinoException(Exception):
        ...

    def __init__(self, user_id, api_key, base_url):
        self.user_id = user_id
        self.api_key = api_key
        self.base_url = base_url

    def __str__(self):
        return 'Neutrino'

    def _generate_params(self, **kwargs):

        params = {
            'user-id': self.user_id,
            'api-key': self.api_key,
        }
        params.update(kwargs)
        # change all keys underscore to dash

        params = {key.replace('_', '-'): value for key,
                  value in params.items()}

        return params

    def _get(self, endpoint, **kwargs):
        params = self._generate_params(**kwargs)
        try:
            response = requests.get(self.base_url + endpoint, params=params)
            if response.ok:
                return response.json()
            else:
                # {'api-error': 2, 'api-error-msg': 'DAILY API LIMIT EXCEEDED'}
                response = response.json()
                if response.get('api-error'):
                    raise self.NeutrinoException(f"NEUTRINO: {response.get('api-error-msg')}")
                else:
                    raise self.NeutrinoException(
                        f'Unknown error: {response.text}')
        except requests.exceptions.RequestException as e:
            raise self.NeutrinoException(e)

    def ip_info(self, ip):
        return self._get('/ip-info', ip=ip)

    def phone_validate(self, number):
        return self._get('/phone-validate', number=number)

    def email_validate(self, email):
        return self._get('/email-validate', email=email)

    def ua_lookup(self, ua):
        return self._get('/ua-lookup', ua=ua)

    def phone_verify(self, phone):
        return self._get('/phone-verify', phone=phone)

    def email_verify(self, email) -> bool:
        response = self._get('/email-verify', email=email)
        # check validity of email according to the API response
        if response.get('valid') and response.get('verified'):
            return True
        return False

    def ip_probe(self, ip):
        return self._get('/ip-probe', ip=ip)

    def ip_bloklist(self, ip, vpn_lookup=False):
        return self._get('/ip-blocklist', ip=ip, vpn_lookup=vpn_lookup)

    def sms_verify(self, number: str, code_length: int = 4, security_code: int = None, counry_code: str = 'en', limit: int = 10, limit_ttl: int = 1) -> dict:
        """
        Send a unique security code to any mobile device via SMS
        ### Arguments
            number: The phone number to send the code to. Must be in E.164 format.
            code_length: The length of the code to send. Must be between 4 and 12 digits.
            security_code: A unique code to identify the request. If not provided, one will be generated.
            country_code: The country code of the phone number. Must be a valid ISO 3166-1 alpha-2 country code.
            limit: The maximum number of times the code can be used. Must be between 1 and 10.
            limit_ttl: The number of days the code is valid for. Must be between 1 and 365.
        ### Returns
            A dictionary containing the security code.

        """

        return self._get('/sms-verify', number=number, code_length=code_length, security_code=security_code, counry_code=counry_code, limit=limit, limit_ttl=limit_ttl)

    def send_sms(self, number: str, message: str) -> dict:
        """
        Send a message to any mobile device via SMS
        ### Arguments
            number: The phone number to send the code to. Must be in E.164 format.
            message: The message to send.
        ### Returns
            whether the message was sent successfully or not.

        """
        return True  # TODO: Implement this

        # return self._get('/send-sms', number=number, message=message)

    def verify_security_code(self, security_code: int, limit_by: str):
        """
        Check if a security code sent via SMS Verify or Phone Verify is valid

        Parameters
        ----------
        ##### security_code : int
            The security code to check.
        ##### limit_by : str
            The type of limit to check. Must be either 'ip' or 'number'.
        """
        return self._get('/verify-security-code', security_code=security_code, limit_by=limit_by)

    def locate(self, ip) -> tuple:
        if settings.DEBUG:
            return self.dummy_locate()
        ip_info = self.ip_info(ip)
        return ip_info.get('valid'), ip_info.get('country-code'), ip_info.get('region'), ip_info.get('city'), ip_info.get('latitude'), ip_info.get('longitude')


    def dummy_locate(self) -> tuple:
        return True, 'US', 'California', 'Mountain View', 37.386, -122.0838