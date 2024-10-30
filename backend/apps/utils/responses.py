from rest_framework import serializers, status
from rest_framework.response import Response


class PanmediaResponse(Response):
    success_key = 'success'
    error_key = 'message'
    HTTP_200_OK, HTTP_201_CREATED, HTTP_202_ACCEPTED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_405_METHOD_NOT_ALLOWED, HTTP_406_NOT_ACCEPTABLE, HTTP_409_CONFLICT, HTTP_410_GONE, HTTP_415_UNSUPPORTED_MEDIA_TYPE, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_500_INTERNAL_SERVER_ERROR = status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_202_ACCEPTED, status.HTTP_204_NO_CONTENT, status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND, status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_406_NOT_ACCEPTABLE, status.HTTP_409_CONFLICT, status.HTTP_410_GONE, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_500_INTERNAL_SERVER_ERROR
    success_responses = (HTTP_200_OK, HTTP_201_CREATED,
                         HTTP_202_ACCEPTED, HTTP_204_NO_CONTENT)
    error_responses = (HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_405_METHOD_NOT_ALLOWED, HTTP_406_NOT_ACCEPTABLE,
                       HTTP_409_CONFLICT, HTTP_410_GONE, HTTP_415_UNSUPPORTED_MEDIA_TYPE, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_500_INTERNAL_SERVER_ERROR)

    HTTP_200_MESSAGE, HTTP_201_MESSAGE, HTTP_202_MESSAGE, HTTP_204_MESSAGE, HTTP_400_MESSAGE, HTTP_401_MESSAGE, HTTP_403_MESSAGE, HTTP_404_MESSAGE, HTTP_405_MESSAGE, HTTP_406_MESSAGE, HTTP_409_MESSAGE, HTTP_410_MESSAGE, HTTP_415_MESSAGE, HTTP_422_MESSAGE, HTTP_500_MESSAGE = 'OK', 'Created', 'Accepted', 'No Content', 'Bad Request', 'Unauthorized', 'Forbidden', 'Not Found', 'Method Not Allowed', 'Not Acceptable', 'Conflict', 'Gone', 'Unsupported Media Type', 'Unprocessable Entity', 'Internal Server Error'


class ErrorResponse(PanmediaResponse):
    ERR_404, ERR_403, ERR_401, ERR_400, ERR_405, ERR_429, ERR_500 = status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED, status.HTTP_400_BAD_REQUEST, status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_429_TOO_MANY_REQUESTS, status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message='', status_code=ERR_404):
        super().__init__({ErrorResponse.success_key: False,
                          self.error_key: str(message)}, status=status_code)


class SuccessResponse(PanmediaResponse):
    def __init__(self, status_code=PanmediaResponse.HTTP_200_OK, **kwargs):
        super().__init__(
            {self.success_key: True, **kwargs}, status=status_code)


class PanmediaResponseSerializer(serializers.Serializer):
    """ This is a sample serializer for showing my intent"""
    success = serializers.BooleanField(
        help_text="Whether the request was successful or not.",
    )


class ErrorResponseSerializer(PanmediaResponseSerializer):
    """ This is a sample serializer for showing my intent"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, many=False)
        self.fields['error'] = serializers.CharField(
            help_text="The error message returned by the request."
        )
        self.fields['success'].default = False


class SuccessResponseSerializer(PanmediaResponseSerializer):
    """ This is a sample serializer for showing my intent"""

    def __init__(self, *args, other_serializer, **kwargs):
        super().__init__(*args, **kwargs, many=False)
        self.fields['data'] = other_serializer(
            help_text="The data returned by the request.",
        )
        self.fields['success'].default = True


class ValidationErrorResponse(PanmediaResponse):
    def __init__(self, validation_errors, status_code=status.HTTP_400_BAD_REQUEST):
        super().__init__({ValidationErrorResponse.success_key: False,
                          'errors': validation_errors}, status=status_code)


class ValidationErrorResponseSerializer(PanmediaResponseSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, many=False)
        self.fields['validation_errors'] = serializers.DictField(
            child=serializers.ListField(
                child=serializers.CharField()
            ),
            help_text="The validation errors returned by the request."
        )
        self.fields['success'].default = False
