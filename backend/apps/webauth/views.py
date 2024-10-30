# view.py
# Create your views here.
from rest_framework.fields import ValidationError
from webauthn import (
    generate_registration_options,
    options_to_json,
    verify_authentication_response,
    verify_registration_response,
    generate_authentication_options,
    base64url_to_bytes,
)
from webauthn.helpers import (
    generate_challenge
)
from webauthn.helpers.exceptions import InvalidRegistrationResponse, InvalidAuthenticationResponse

from webauthn.helpers.structs import (
    RegistrationCredential,
    AuthenticationCredential,
    UserVerificationRequirement,
)


from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from rest_framework.response import Response

from .models import WebauthnCredentials, WebauthnRegistration, WebAuthDevice
import json

from rest_framework import viewsets
from rest_framework.decorators import action
from .serializers import WebauthnCredentialsSerializer, WebauthnRegistrationSerializer


# disable csrf for this view
from django.views.decorators.csrf import csrf_exempt
from secrets import token_hex
from django.conf import settings

# import http status codes
from rest_framework import status
from base64 import b64decode, b64encode

from django.utils.decorators import method_decorator
class WebAuthRegistrationViewSet(viewsets.ViewSet):
    
    def register(self, request):
        """
        GET request to get the registration options
        """
        
        # check if the user has already registered a device
        if WebAuthDevice.objects.filter(user=request.user).exists():
            return Response({'error': 'User already registered'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        challenge = generate_challenge()

        public_credential_creation_options = generate_registration_options(
            rp_id=settings.WEBAUTH_RP_ID,
            rp_name=settings.WEBAUTH_RP_NAME,
            user_id=str(user.id),
            user_name=request.user.username,
            challenge=challenge,
        )

        # save the challenge in the session
        request.session["challenge"] = b64encode(challenge).decode()

        # The options are encoded in bytes - to save them correctly
        # I use the json strings
        options_dict = json.loads(options_to_json(
            public_credential_creation_options))

        return Response(options_dict)

    def verify(self, request):
        # get the challenge from the session
        encoded_challenge = request.session.get("challenge", None)

        if encoded_challenge is None:
            messages.error(request, "Invalid authentication data.")
            return HttpResponse(status=400)

        challenge = b64decode(encoded_challenge)

        data = request.data
        try:
            credential = RegistrationCredential.parse_raw(json.dumps(data))
        except ValidationError:
            messages.error(request, "Invalid authentication data.")
            return HttpResponse(status=400)

        try:
            verification = verify_registration_response(
                credential=credential,
                expected_challenge=challenge,
                expected_origin=settings.WEBAUTH_ORIGIN,
                expected_rp_id=settings.WEBAUTH_RP_ID,
                require_user_verification=False,
            )
        except InvalidRegistrationResponse as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

        # save the credential

        web_device = WebAuthDevice.objects.create(
            user=request.user,
            name='test',
            credential_id=verification.credential_id,
            public_key=verification.credential_public_key,
            format=verification.fmt,
            type=verification.credential_type,
            sign_count=verification.sign_count,
        )

        return Response(status=status.HTTP_201_CREATED)


class WebAuthnAuthenticationViewSet(viewsets.ViewSet):

    # @method_decorator(login_required)
    def authenticate(self, request):
        """
        GET request to get the authentication options.
        """
        user = request.user

        # Fetch the user's registered WebAuthn credentials
        credentials = WebAuthDevice.objects.filter(user=user)

        if not credentials.exists():
            return Response({'error': 'No registered credentials'}, status=status.HTTP_404_NOT_FOUND)

        allow_credentials = [{
            'type': 'public-key',
            # Decode the credential ID
            'id': base64url_to_bytes(cred.credential_id)
        } for cred in credentials]

        # Generate authentication options
        options = generate_authentication_options(
            rp_id=settings.WEBAUTH_RP_ID,

            # allow_credentials=allow_credentials,
            user_verification=UserVerificationRequirement.PREFERRED,
        )

        # Save the challenge in the session
        request.session["authentication_challenge"] = b64encode(
            options.challenge).decode()

        options_dict = json.loads(options_to_json(options))

        # Convert options to JSON and return
        return Response(options_dict)

    # @method_decorator(login_required)

    def verify(self, request):
        """
        POST request to verify the authentication response.
        """
        # Get the challenge from the session
        encoded_challenge = request.session.get(
            "authentication_challenge", None)

        if encoded_challenge is None:
            return Response({'error': 'Challenge not found or expired'}, status=status.HTTP_400_BAD_REQUEST)

        challenge = b64decode(encoded_challenge)

        # Parse the response
        data = request.data
        try:
            credential = AuthenticationCredential.parse_raw(json.dumps(data))
        except ValidationError:
            return Response({'error': 'Invalid authentication data'}, status=status.HTTP_400_BAD_REQUEST)

        # Verify the response
        try:
            device = WebAuthDevice.objects.get(credential_id=credential.raw_id)

            verification = verify_authentication_response(
                credential=credential,
                expected_challenge=challenge,
                expected_origin=settings.WEBAUTH_ORIGIN,
                expected_rp_id=settings.WEBAUTH_RP_ID,
                credential_public_key=device.public_key,
                credential_current_sign_count=device.sign_count,
                require_user_verification=False,  # or True if strong auth is needed
            )

            # Update the sign count in the database
            device.sign_count = verification.new_sign_count
            device.save()

            # Authentication successful
            return Response({'status': 'Authentication successful'}, status=status.HTTP_200_OK)

        except InvalidAuthenticationResponse as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
