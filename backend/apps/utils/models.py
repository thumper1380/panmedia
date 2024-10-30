from polymorphic_tree.models import PolymorphicMPTTModel, PolymorphicTreeForeignKey
from rest_framework import status
from rest_framework.response import Response
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from polymorphic_tree.managers import PolymorphicMPTTModelManager, PolymorphicMPTTQuerySet
# import polymorphic mptt model


class LogQuerySet(models.QuerySet):
    ...


class LogManager(models.Manager):
    def get_queryset(self):
        return LogQuerySet(self.model, using=self._db)


class Log(models.Model):
    BLUE, GREEN, YELLOW, RED = '#9ec5fe', '#28a745', '#ffc107', '#dc3545'

    objects = LogManager()
    DEBUG, INFO, WARNING, ERROR = 'debug', 'info', 'warning', 'error'
    LEVEL_CHOICES = (
        (DEBUG, 'DEBUG'),
        (INFO, 'INFO'),
        (WARNING, 'WARNING'),
        (ERROR, 'ERROR'),
    )

    LEVEL_COLORS = {
        DEBUG: GREEN,
        INFO: BLUE,
        WARNING: YELLOW,
        ERROR: RED,
    }

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    message = models.TextField()
    level = models.CharField(max_length=32, choices=LEVEL_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message

    @property
    def level_name(self):
        return self.get_level_display()

    @property
    def model_name(self):
        return self.content_type.model_class().__name__

    @property
    def color(self):
        return self.LEVEL_COLORS[self.level]

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Log'
        verbose_name_plural = 'Logs'


class LogModelQuerySet:
    def logs(self, level=None):
        # get all logs for this model
        logs = Log.objects.filter(
            content_type=ContentType.objects.get_for_model(self.model))
        # filter by level if provided
        if level:
            logs = logs.filter(level=level)
        return logs


class LogModelManager:
    def get_queryset(self):
        return LogModelQuerySet(self.model, using=self._db)

    def logs(self, level=None):
        return self.get_queryset().logs(level=level)




class LogModel:
    objects = LogModelManager()

    def log_message(self, message, level=Log.INFO):
        log = Log(content_object=self, message=message,
                     level=level)
        log.save()

    def debug(self, message):
        self.log_message(message, Log.DEBUG)

    def info(self, message):
        self.log_message(message, Log.INFO)

    def warning(self, message):
        self.log_message(message, Log.WARNING)

    def error(self, message):
        self.log_message(message, Log.ERROR)

    def logs(self, level=None):
        # get all logs for this model
        logs = Log.objects.filter(
            content_type=ContentType.objects.get_for_model(self), object_id=self.id)
        # filter by level if provided
        if level:
            logs = logs.filter(level=level)
        return logs

    def __str__(self):
        return f'{self.__class__.__name__}'


class LogModelMixin(LogModel, models.Model):
    class Meta:
        abstract = True



class LogPolymorphicMPTTQuerySet(LogModelQuerySet, PolymorphicMPTTQuerySet): ...

class LogPolymorphicMPTTManager(LogModelManager, PolymorphicMPTTModelManager):
    def get_queryset(self):
        return LogPolymorphicMPTTQuerySet(self.model, using=self._db)


class LogPolymorphicMPTTModelMixin(LogModel, PolymorphicMPTTModel):
    objects = LogPolymorphicMPTTManager()
    class Meta:
        abstract = True


# class LogPolymorphicMPTTModelMixin()


class MainResponse(Response):
    key = 'success'
    HTTP_200_OK, HTTP_201_CREATED, HTTP_202_ACCEPTED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_405_METHOD_NOT_ALLOWED, HTTP_406_NOT_ACCEPTABLE, HTTP_409_CONFLICT, HTTP_410_GONE, HTTP_415_UNSUPPORTED_MEDIA_TYPE, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_500_INTERNAL_SERVER_ERROR = status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_202_ACCEPTED, status.HTTP_204_NO_CONTENT, status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND, status.HTTP_405_METHOD_NOT_ALLOWED, status.HTTP_406_NOT_ACCEPTABLE, status.HTTP_409_CONFLICT, status.HTTP_410_GONE, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_500_INTERNAL_SERVER_ERROR
    SUCCESS_RESPONSES = (HTTP_200_OK, HTTP_201_CREATED,
                         HTTP_202_ACCEPTED, HTTP_204_NO_CONTENT)
    ERROR_RESPONSES = (HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_405_METHOD_NOT_ALLOWED, HTTP_406_NOT_ACCEPTABLE,
                       HTTP_409_CONFLICT, HTTP_410_GONE, HTTP_415_UNSUPPORTED_MEDIA_TYPE, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_500_INTERNAL_SERVER_ERROR)

    HTTP_200_MESSAGE, HTTP_201_MESSAGE, HTTP_202_MESSAGE, HTTP_204_MESSAGE, HTTP_400_MESSAGE, HTTP_401_MESSAGE, HTTP_403_MESSAGE, HTTP_404_MESSAGE, HTTP_405_MESSAGE, HTTP_406_MESSAGE, HTTP_409_MESSAGE, HTTP_410_MESSAGE, HTTP_415_MESSAGE, HTTP_422_MESSAGE, HTTP_500_MESSAGE = 'OK', 'Created', 'Accepted', 'No Content', 'Bad Request', 'Unauthorized', 'Forbidden', 'Not Found', 'Method Not Allowed', 'Not Acceptable', 'Conflict', 'Gone', 'Unsupported Media Type', 'Unprocessable Entity', 'Internal Server Error'

    def __init__(self, message, status=200):
        super().__init__({MainResponse.key: False,
                          'error': str(message)}, status=status)

    def is_success(self):
        return self.status_code in self.SUCCESS_RESPONSES
