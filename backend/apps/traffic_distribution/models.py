import bisect
from .choices import RuleChoices
from .managers import SettingsTemplateQuerySet, ResponseQuerySet
from apps.settings.models import LeadProfile
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json
import random
import re
import requests
import string
import sys

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import F, Q, OuterRef, Subquery, Sum
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.template import Context, Template
from django.utils.translation import gettext_lazy as _
from polymorphic.models import PolymorphicModel

from .exceptions import (
    AdvertiserCapIsFull, AdvertiserCapNotExist,
    AdvertiserRejectedException, ResponseException,
    CapFolderDoesNotExist, UnknowError
)

from .messages import ADVERTISER_REJECT_MESSAGE, DUMMY_REJECT_MESSAGE

from .managers import (
    GroupQuerySet, SettingsTemplateQuerySet,
    CapFolderQuerySet, RotationControlQuerySet, AdvertiserFolderQuerySet, SplitFolderQuerySet
)

from apps.utils.folders import (
    AdvertiserFolder, AffiliateFolder,
    CountryFolder, Folder, TargetFolder
)
from apps.utils.models import LogModelMixin


from django.conf import settings


def func_name(n=0): return sys._getframe(n + 1).f_code.co_name


class BaseSuccessResponse:
    pass


class SuccessPushResponse(BaseSuccessResponse):
    def __init__(self, advertiser_lead_id, auto_login):
        self.advertiser_lead_id = advertiser_lead_id
        self.auto_login = auto_login


class GroupTemplate(models.Model):
    objects = GroupQuerySet.as_manager()
    name = models.CharField(max_length=255)
    provider = models.ForeignKey(
        'Provider', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'Group #{self.id}'

    class Meta:
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'

    def get_all_settings(self):
        return SettingsTemplate.objects.filter(group__in=self).annotate(key=F('name'))


class SettingsTemplate(models.Model):
    objects = SettingsTemplateQuerySet.as_manager()
    name = models.CharField(max_length=255)
    group = models.ForeignKey(GroupTemplate, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Setting'
        verbose_name_plural = 'Settings'

    def __str__(self):
        return f'{self.name}'


class APIConnection(models.Model):
    advertiser = models.ForeignKey(
        'Advertiser', on_delete=models.CASCADE, null=True, blank=True)
    group_template = models.ForeignKey(
        GroupTemplate, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        """Meta definition for APIConnection."""

        verbose_name = 'API Connection'
        verbose_name_plural = 'API Connection'

    def __str__(self):
        return f'{self.group_template.name}'


class Settings(models.Model):
    api_connection = models.ForeignKey(
        APIConnection, on_delete=models.CASCADE, null=True, blank=True)
    template = models.ForeignKey(
        SettingsTemplate, on_delete=models.CASCADE, null=True, blank=True)
    value = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        """Meta definition for Settings."""

        verbose_name = 'Settings'
        verbose_name_plural = 'Settings'

    def __str__(self):
        return ''


class ResponseKey(models.Model):
    class KeyType(models.TextChoices):
        ADVERTISER_EXTERNAL_ID, AUTO_LOGIN_URL, SALE_STATUS, ADV_SUB_1, ADV_SUB_2, ADV_SUB_3, ADV_SUB_4, ADV_SUB_5 = 'advertiser_external_id', 'auto_login_url', 'sale_status', 'adv_sub_1', 'adv_sub_2', 'adv_sub_3', 'adv_sub_4', 'adv_sub_5'

    key = models.CharField(max_length=30, blank=True,
                           null=True, choices=KeyType.choices)
    response = models.ForeignKey(
        'Response', related_name='keys', on_delete=models.CASCADE, null=True, blank=True)
    value = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        """Meta definition for Key."""

        verbose_name = 'Key'
        verbose_name_plural = 'Keys'

    def __str__(self):
        return f'{self.key} - {self.value}'


class Response(PolymorphicModel):
    objects = ResponseQuerySet.as_manager()

    def __init__(self, *args, **kwargs):
        self.response = None
        self.caller = None
        super().__init__(*args, **kwargs)

    class StatusCodes(models.TextChoices):
        _200, _201, _202, _204, _400, _401, _403, _404, _405, _406, _408, _409, _410, _500, _501, _502, _503, _504 = 200, 201, 202, 204, 400, 401, 403, 404, 405, 406, 408, 409, 410, 500, 501, 502, 503, 504

    class Meta:
        verbose_name = 'Response'
        verbose_name_plural = 'Responses'
        unique_together = ('status_code', 'request')

    class Type(models.TextChoices):
        ARRAY, OBJECT, STRING, NUMBER, BOOLEAN = 'ARRAY', 'OBJECT', 'STRING', 'NUMBER', 'BOOLEAN'

    class ResponseException(Exception):
        ...

    class KeyDoesNotExist(ResponseException):
        ...

    request = models.ForeignKey(
        'Request', related_name='responses', on_delete=models.CASCADE, null=True, blank=True)

    type = models.CharField(max_length=30, blank=True,
                            null=True, choices=Type.choices)

    status_code = models.CharField(
        max_length=3, choices=StatusCodes.choices, blank=True, null=True)

    def _keys(self):
        keys = self.keys.all()
        return {key.key: key.value for key in keys}

    def extract_array(self, j_res, **kwargs):
        if not kwargs:
            kwargs = self._keys()
        extracted = []
        if isinstance(j_res, list):
            for item in j_res:
                if isinstance(item, dict) and any(v in item for v in kwargs.values()):
                    extracted.append(
                        {k: item[v] for k, v in kwargs.items() if v in item})
                extracted.extend(self.extract_array(item, **kwargs))
        elif isinstance(j_res, dict):
            for key, nested_value in j_res.items():
                extracted.extend(self.extract_array(nested_value, **kwargs))
        return extracted

    def extract_values(self, j_res, key):
        result = []
        if isinstance(j_res, dict):
            for k, v in j_res.items():
                if k == key:
                    result.append(v)
                else:
                    result.extend(self.extract_values(v, key))
        elif isinstance(j_res, list):
            for item in j_res:
                result.extend(self.extract_values(item, key))

        return result

    @property
    def is_success(self):
        return self.status_code in [self.StatusCodes._200, self.StatusCodes._201, self.StatusCodes._202, self.StatusCodes._204]

    @property
    def is_error(self):
        return not self.is_success

    def __str__(self):
        return str(self.status_code)

    @property
    def text(self):
        return self.response.text

    def json(self) -> BaseSuccessResponse:
        if not self.response.ok or not self.caller:  # unsuccessful response
            raise ResponseException(self.response.text)

        # response is successful

        if self.caller == 'PullConversionsRequest':
            return self.extract_values(self.response.json(), self._keys().get(ResponseKey.KeyType.ADVERTISER_EXTERNAL_ID))
        elif self.caller == 'PullLeadsRequest':
            return self.extract_array(self.response.json(), **self._keys())
        elif self.caller == 'PushLeadRequest':
            # check if advertiser_external_id and auto_login_url is in keys
            if not all(k in self._keys() for k in [ResponseKey.KeyType.AUTO_LOGIN_URL, ResponseKey.KeyType.ADVERTISER_EXTERNAL_ID]):
                raise self.KeyDoesNotExist(
                    'Keys advertiser_external_id and auto_login_url are required')

            res = self.response.json()

            auto_login_url_key = self._keys().get(ResponseKey.KeyType.AUTO_LOGIN_URL)
            advertiser_external_id_key = self._keys().get(
                ResponseKey.KeyType.ADVERTISER_EXTERNAL_ID)

            auto_login_url = res.get(auto_login_url_key)
            advertiser_external_id = res.get(advertiser_external_id_key)

            return SuccessPushResponse(
                advertiser_lead_id=advertiser_external_id, auto_login=auto_login_url)


class Header(models.Model):
    key = models.CharField(max_length=50, blank=True)
    value = models.CharField(max_length=50, blank=True, null=True)
    request = models.ForeignKey(
        'Request', on_delete=models.CASCADE, null=True, blank=True, related_name='headers')

    class Meta:
        """Meta definition for RequestHeader."""

        verbose_name = 'Request Header'
        verbose_name_plural = 'Request Headers'

    def __str__(self):
        return self.key


class Request(PolymorphicModel):
    class RequestException(Exception):
        ...

    class MethodChoices(models.TextChoices):
        GET, POST, PUT, PATCH, DELETE = 'GET', 'POST', 'PUT', 'PATCH', 'DELETE'

    method = models.CharField(
        max_length=10, choices=MethodChoices.choices, default=MethodChoices.GET)
    body = models.JSONField(blank=True, null=True)
    url = models.CharField('URL', max_length=250)
    path = models.CharField('Path', max_length=250)

    @staticmethod
    def urlencode(dict):
        query_params = '&'.join(
            [f'{key}={value}' for key, value in dict.items()])
        return query_params[1:] if query_params.startswith('&') else query_params

    def render(self, text: str, context: dict) -> str:
        """
        Render a template string with the given context.
        """
        template = Template(text)
        return template.render(Context(context))

    def get_body(self, *args, **kwargs):
        body = self.body
        try:
            for key, value in body.items():
                if isinstance(value, str) and "{{" in value and "}}" in value:
                    # search for {{DAY(x)}} or {{MONTH(x)}} or {{YEAR(x)}}
                    match = re.match(
                        r'{{(DAYS|MONTHS|YEARS)\((\d+)\)}}', value)
                    if match:
                        period, value = match.groups()
                        period = period.lower()
                        value = int(value)
                        print('period: ', period, 'value: ', value)
                        self.provider: Provider
                        date = self.provider.calc_date(period, value)
                        body[key] = date

            body = json.dumps(body)
            rendered_body = self.render(body, kwargs)
            return rendered_body
        except Exception as e:
            self.provider.error(f'Error rendering body: {e}')
            return self.body

    def get_headers(self, *args, **kwargs):
        headers = {header.key: self.render(
            header.value, kwargs) for header in self.headers.all()}
        # add custom headers
        headers.update({'class': self.__class__.__name__})
        return headers

    def get_url(self, *args, **kwargs):
        url = self.url + self.path
        body = self.get_body(**kwargs)
        if self.method == self.MethodChoices.GET:
            url = self.url + self.path + '?' + \
                self.urlencode(json.loads(body))
            # join url and query params

        return self.render(url, kwargs)

    def execute(self, *args, **kwargs):
        headers = self.get_headers(**kwargs)
        body = json.loads(self.get_body(**kwargs))
        url = self.get_url(**kwargs)
        response = requests.request(
            method=self.method,
            url=url,
            headers=headers,
            data=body if self.method != self.MethodChoices.GET else None,
        )

        response_obj = self.responses.get_response(response)
        if response_obj.is_success:
            self.provider.debug(
                f'Successfully executed {self.method} request to {self.provider}')
            return response_obj
        else:
            self.provider.error(
                f'Error while executing {self.method} request to {self.get_url(**kwargs)}: {response.status_code} - {response.text} body: {self.get_body(**kwargs)}, headers: {self.get_headers(**kwargs)}')
            return response_obj

    def __str__(self):
        return f'{self.method}'


class PullConversionsRequest(Request):
    provider = models.OneToOneField(
        'Provider', on_delete=models.CASCADE, null=True, blank=True, related_name='pull_conversions_request')

    class Meta:
        verbose_name = 'Pull Conversions Request'
        verbose_name_plural = 'Pull Conversions Request'


class PullLeadsRequest(Request):
    provider = models.OneToOneField(
        'Provider', on_delete=models.CASCADE, null=True, blank=True, related_name='pull_leads_request')

    class Meta:
        verbose_name = 'Pull Leads Request'
        verbose_name_plural = 'Pull Leads Request'


class PushLeadRequest(Request):
    provider = models.OneToOneField(
        'Provider', on_delete=models.CASCADE, null=True, blank=True, related_name='push_lead_request')

    class Meta:
        verbose_name = 'Push Lead Request'
        verbose_name_plural = 'Push Leads Request'


class Provider(LogModelMixin):
    class DateFormats(models.TextChoices):
        DD_MM_YYYY = '%d-%m-%Y', 'dd-mm-yyyy'
        MM_DD_YYYY = '%m-%d-%Y', 'mm-dd-yyyy'
        YYYY_MM_DD = '%Y-%m-%d', 'yyyy-mm-dd'

    name = models.CharField(max_length=30)
    date_format = models.CharField(
        max_length=30, choices=DateFormats.choices, default=DateFormats.DD_MM_YYYY)

    is_active = models.BooleanField(default=True, verbose_name='Active')
    is_test = models.BooleanField(default=False, verbose_name='Test')

    class Meta:
        '''Meta definition for Provider.'''
        verbose_name = 'Provider'
        verbose_name_plural = 'Providers'

    def calc_date(self, period: str, value: str) -> str:
        try:
            date = datetime.now() - relativedelta(**{period: int(value)})
            return date.strftime(self.date_format)

        except Exception:
            return ''

    def _validate_password(self, password: str) -> bool:
        '''Validate if password contains at least one number and one uppercase letter one lowercase letter one symbol and length should be between 8-10'''
        if len(password) < 8 or len(password) > 10:
            return False
        if not any(char.isdigit() for char in password):
            return False
        if not any(char.isupper() for char in password):
            return False
        if not any(char.islower() for char in password):
            return False
        return True

    def _generate_password(self) -> str:
        while True:
            password = ''.join(random.choice(
                string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(10))
            if self._validate_password(password):
                return password

    def __str__(self) -> str:
        return self.name

    def pull_conversions(self, *args, **kwargs):
        request: Request = self.pull_conversions_request
        return request.execute(**kwargs)

    def pull_leads(self, *args, **kwargs):
        request: Request = self.pull_leads_request
        return request.execute(**kwargs)

    def push_lead(self, *args, **kwargs):
        request: Request = self.push_lead_request
        return request.execute(**kwargs)

    @receiver(post_save)
    def create_settings(sender, instance, created, **kwargs):
        if sender == Provider:
            for advertiser in instance.advertiser_set.all():
                advertiser.save()

    @receiver(pre_save)
    def check_requests(sender, instance, **kwargs):
        if sender == Provider:
            ...
            # if not instance.pull_conversions_request or not instance.pull_leads_request or not instance.push_lead_request:
           #     raise Request.RequestException(
           #         'Provider must have all requests set up')

           # instance.save()

    def export_settings(self):
        from .serializers import ProviderSerializer
        serialized_provider = ProviderSerializer(self).data
        from rest_framework.renderers import JSONRenderer
        return JSONRenderer().render(serialized_provider)

    def get_response(self, request_type, status_code):  # TODO:  fix this
        try:
            request_obj = self.request_set.get(type=request_type)
        except Request.DoesNotExist:
            raise Request.RequestException(
                f'Request does not exist for {request_type}')
        try:
            response_obj = request_obj.response_set.get(
                status_code=status_code)
        except Response.DoesNotExist:
            raise Response.ResponseException(
                f'Response does not exist for {request_type} with status code {status_code}')
        return response_obj


class Assigned(models.Model):
    label = models.CharField(max_length=30)
    sale_status_mapping = models.ForeignKey(
        'SaleStatusMapping', on_delete=models.CASCADE, related_name='assigned')

    def __str__(self):
        return self.label


class Unassigned(models.Model):
    label = models.CharField(max_length=30)
    advertiser = models.ForeignKey(
        'Advertiser', on_delete=models.CASCADE, related_name='unassigned')

    def __str__(self) -> str:
        return self.label


class SaleStatusMapping(models.Model):

    sale_status = models.ForeignKey(
        'settings.SaleStatus', on_delete=models.CASCADE)
    advertiser = models.ForeignKey(
        'Advertiser', on_delete=models.CASCADE, related_name='sale_status_mappings')

    def __str__(self):
        return self.sale_status.name

    @property
    def unassigned(self):
        return self.advertiser.unassigned

    def add_assigned(self, label):
        self.assigned.create(label=label)
        # remove from unassigned
        self.advertiser.unassigned.filter(label=label).delete()


class AdvertiserRequiredField(models.Model):
    label = models.CharField(max_length=30)
    key = models.CharField(max_length=30)
    field = models.ForeignKey(
        LeadProfile, on_delete=models.CASCADE, related_name='advertiser_required_fields')
    advertiser = models.ForeignKey(
        'Advertiser', on_delete=models.CASCADE, related_name='required_fields')

    def __str__(self) -> str:
        return self.label

    class Meta:
        verbose_name = 'Advertiser Required Field'
        verbose_name_plural = 'Advertiser Required Fields'
        unique_together = (('field', 'advertiser',), ('key', 'advertiser',))


class Advertiser(models.Model):
    class CurrencyChoices(models.TextChoices):
        EUR, USD = 'EUR', 'USD'

    name = models.CharField(max_length=30)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    default_currency = models.CharField(
        'Default Currency', max_length=3, choices=CurrencyChoices.choices, default=CurrencyChoices.USD)
    goal = models.ForeignKey('settings.Goal', on_delete=models.CASCADE,)

    auto_generated_password = models.BooleanField(default=False, verbose_name='Auto Generated Password',
                                                  help_text='If checked and password is not set, password will be generated automatically')

    is_test = models.BooleanField(default=False, verbose_name='Test')
    is_active = models.BooleanField(default=True, verbose_name='Active')
    created_at = models.DateTimeField(auto_now_add=True)

    def get_password(self):
        password_required = self.required_fields.filter(
            key='password').exists()  # TODO:  fix this
        if self.auto_generated_password and password_required:
            return self.provider._generate_password()

    def __str__(self):
        return self.name

    def get_goal(self):
        return self.goal

    @property
    def __settings__(self):
        settings = Settings.objects.filter(
            api_connection__advertiser=self).values_list('template__name', 'value')
        _set = {setting[0]: setting[1] for setting in settings}
        return _set

    def pull_conversions(self):
        if not self.is_test:
            return self.provider.pull_conversions(**self.__settings__)

    def pull_leads(self):
        if not self.is_test:
            return self.provider.pull_leads(**self.__settings__)

    def generate_advertiser_lead_id(self):
        return random.randint(10000000000000, 999999999999999)

    def raise_rejection_exception(self, message: str, exepction: Exception = AdvertiserRejectedException):
        raise exepction(
            ADVERTISER_REJECT_MESSAGE.format(advertiser_name=self.name, advertiser_id=self.id) + message)

    def push_lead(self, lead, reject=False) -> bool:
        """
        Pushes a lead to the provider.

        Args:
            lead: The lead object to be pushed.
            reject: A boolean indicating whether to reject the lead.

        Returns:
            If `is_test` is True, returns a tuple containing the advertiser_lead_id and auto_login.
            Otherwise, returns a tuple containing the response_data[0] and response_data[1].

        Raises:
            ResponseException: If an exception occurs while pushing the lead.
            UnknowError: If an unknown error occurs while pushing the lead.
        """
        if self.is_test:
            if reject:
                return self.raise_rejection_exception(DUMMY_REJECT_MESSAGE)

            advertiser_lead_id = self.generate_advertiser_lead_id()
            auto_login = settings.DEFAULT_ADVERTISER_TEST_AUTOL_OGIN_URL
            return advertiser_lead_id, auto_login

        try:
            serializer_data = lead.get_serialized_data()
            response = self.provider.push_lead(
                **{**self.__settings__, **serializer_data})

            response_data = response.json()

            success_push_response = SuccessPushResponse(
                advertiser_lead_id=response_data[0], auto_login=response_data[1])

            return response_data[0], response_data[1]
        except ResponseException as e:
            self.raise_rejection_exception(str(e))
        except Exception as e:
            self.raise_rejection_exception(str(e), UnknowError)

    def get_sale_statuses(self):
        return self.sale_status_mappings.all()

    def leads(self, *args, **kwargs) -> models.QuerySet:
        # get all advertiser leads that the trafficdata state is not in [sale]
        return self.trafficdata.filter(~Q(state='sale'), **kwargs)

    @ property
    def unassigned(self):
        return self.unassigned.all()

    def method(self, *args, **kwargs) -> str:
        return Request.objects.get(provider=self.provider, **kwargs).method

    def url(self, *args, **kwargs) -> str:
        request = Request.objects.get(provider=self.provider, **kwargs)
        return self.get_value(request.url) + self.get_value(request.path)

    def add_unassigned_status(self, status):
        if not self.unassigned.filter(label=status).exists():
            return self.unassigned.create(label=status)

    def assign_sale_status(self, status_obj, status_txt):
        # Import here to avoid circular imports
        from apps.settings.models import SaleStatus
        # Check if sale_status is an instance of SaleStatus or a primary key
        if not isinstance(status_obj, SaleStatus):
            status_obj = SaleStatus.objects.get(name=status_obj)
        # Check if sale_status is already assigned to this advertiser
        if not self.sale_status_mappings.filter(sale_status=status_obj).exists():
            status_mapping: SaleStatusMapping = self.sale_status_mappings.create(
                sale_status=status_obj)
            status_mapping.add_assigned(status_txt)
        else:
            status_mapping: SaleStatusMapping = self.sale_status_mappings.get(
                sale_status=status_obj)
            status_mapping.add_assigned(status_txt)

    def get_response(self, response_type, status_code):
        provider_response = self.provider.get_response(
            response_type, status_code)
        return provider_response

    def fill_cap(self, advertiser_folder: AdvertiserFolder) -> bool:
        return advertiser_folder.get_descendants(include_self=False).filter(capfolder__isnull=False)


class RotationControl(Folder):
    objects = RotationControlQuerySet.as_manager()

    class Meta:
        verbose_name = _("Rotation Control")
        verbose_name_plural = _("Rotation Control")

    def tree(self, folder, advertisers_ids, **kwargs) -> list:
        if not folder.is_active:
            return

        if isinstance(folder, TargetFolder):
            try:
                advertisers_folder = folder.select_advertiser()
                advertisers_ids.append(advertisers_folder.id)
            except AdvertiserCapIsFull:
                pass
            return

        for child in folder.get_children():
            if child.pass_rule(**kwargs):
                self.tree(folder=child,
                          advertisers_ids=advertisers_ids, **kwargs)

        return advertisers_ids

    @ classmethod
    def reset_caps(cls):
        # this method is used to reset CapFolder of RotationControl
        CapFolder.objects.reset()

    @ classmethod
    def search(cls, **kwargs) -> CapFolderQuerySet:
        roots = cls.objects.filter(parent__isnull=True)
        advertiser_ids = []
        for root in roots:
            if root.pass_rule(**kwargs):
                root.tree(root, advertiser_ids, **kwargs)

        return CapFolder.objects.filter(parent__in=advertiser_ids).order_by('tree_id', 'lft', 'level')


class RotationContolAffiliateFolder(RotationControl, AffiliateFolder):
    class Meta:
        verbose_name = _("Affiliate Folder")
        verbose_name_plural = _("Affiliate Folders")


class RotationControlCountryFolder(RotationControl, CountryFolder):
    class Meta:
        verbose_name = _("Country Folder")
        verbose_name_plural = _("Country Folders")


class SplitFolder(RotationControl):
    objects = SplitFolderQuerySet.as_manager()

    can_have_children = True
    can_be_root = True
    can_have_siblings = True

    @ property
    def icon(self):
        return 'https://foxesmedia-ld.platform500.com/assets/img/rotation-trees/ico/AB.svg'

    def get_advertiser_folders(self):
        return self.get_children().instance_of(RotationControlAdvertiserSplit)

    @ property
    def total_weight(self):
        return self.get_advertiser_folders().aggregate(Sum('rotationcontroladvertisersplit__weight'))['rotationcontroladvertisersplit__weight__sum']

    def select_advertiser(self) -> 'AdvertiserFolder':
        # choose relevant advertiser according to weight

        capfolder_subquery = CapFolder.objects.filter(
            parent_id=OuterRef('id'),
            current_amount__lt=F('cap_amount')
        )

        children = list(
            RotationControlAdvertiserSplit.objects.filter(
                parent=self,
                weight__gt=0,
                id__in=Subquery(capfolder_subquery.values('parent_id'))
            )
        )

        if not children:  # New condition here
            return None

        total_weight = sum(child.weight for child in children)

        if total_weight == 0:
            return None

        weights = [0] + [child.weight for child in children]
        for i in range(1, len(weights)):
            weights[i] += weights[i-1]

        random_number = random.randint(0, total_weight - 1)

        # Binary search to find the child corresponding to the random number
        child_idx = bisect.bisect_right(weights, random_number) - 1
        return children[child_idx]


class CapFolder(TargetFolder, RotationControl):
    class Meta:
        verbose_name = _("Cap Folder")
        verbose_name_plural = _("Cap Folders")

    objects = CapFolderQuerySet.as_manager()

    class TypeChoices(models.TextChoices):
        REGULAR = 'regular', _('Regular')
        DROP_ON_REJECT = 'drop_on_reject', _('Drop on reject')

    cap_amount = models.PositiveIntegerField(default=1000)
    current_amount = models.PositiveIntegerField(default=0)
    cap_type = models.CharField(
        max_length=255, choices=TypeChoices.choices, default=TypeChoices.REGULAR)

    def is_full(self):
        return self.current_amount == self.cap_amount

    def fill(self, success: bool = True):
        if self.cap_type == self.TypeChoices.DROP_ON_REJECT and success or self.cap_type == self.TypeChoices.REGULAR:
            self.increament()

    def reset(self):
        self.current_amount = 0
        self.save()

    def increament(self):
        self.current_amount += 1
        self.save()

    @property
    def advertiser(self):
        parent = getattr(self, 'parent', None)
        if isinstance(parent, (RotationControlAdvertiserFolder, RotationControlAdvertiserSplit)):
            return parent.advertiser
        raise AdvertiserCapNotExist(
            _(f'Advertiser Cap does not exist for this cap folder {self.id}')
        )

    def clean(self):
        if self.cap_amount < 0:
            raise ValidationError(
                {'cap_amount': _('Cap amount cannot be negative')})
        if self.current_amount > self.cap_amount:
            raise ValidationError(
                {'current_amount': _('Current amount cannot be greater than cap amount')})

    @ property
    def icon(self):
        return 'https://foxesmedia-ld.platform500.com/assets/img/rotation-trees/ico/C.svg'

    def send_lead_to_advertiser(self, lead) -> 'CapFolder':
        """
        Sends a lead to the advertiser associated with the parent folder of this CapFolder instance.
        If the parent folder does not have an advertiser, an exception is raised.

        Args:
            lead: The lead to be sent to the advertiser.

        Returns:
            A tuple containing the CapFolder instance, the advertiser lead ID, and a boolean indicating whether
            the advertiser requires an auto-login.

        Raises:
            Exception: If the parent folder of this CapFolder instance is not of type RotationControlAdvertiserFolder
                or RotationControlAdvertiserSplit, or if the parent folder does not have an advertiser.
        """
        # Find the parent instance, which can be either RotationControlAdvertiserFolder or RotationControlAdvertiserSplit
        parent = self.parent

        if isinstance(parent, (RotationControlAdvertiserFolder, RotationControlAdvertiserSplit)):
            # If parent has an advertiser
            if hasattr(parent, 'advertiser'):
                advertiser: Advertiser = parent.advertiser
                # Assuming advertiser has a method 'process_lead'
                advertiser_lead_id, auto_login = advertiser.push_lead(lead)
                return self, advertiser_lead_id, auto_login
            else:
                raise Exception(
                    f'Parent folder {parent.id} does not have an advertiser')
        else:
            raise Exception(
                f'CapFolder #{self.id} does not have a parent of type RotationControlAdvertiserFolder or RotationControlAdvertiserSplit')


class RotationControlAdvertiserFolder(TargetFolder, RotationControl, AdvertiserFolder):
    objects = AdvertiserFolderQuerySet.as_manager()
    child_types = [CapFolder,]
    can_have_children = True

    class Meta:
        verbose_name = _("Advertiser Folder")
        verbose_name_plural = _("Advertiser Folders")

    @ property
    def icon(self):
        return 'https://foxesmedia-ld.platform500.com/assets/img/rotation-trees/ico/A.svg'

    @ receiver(post_save)
    def add_cap_folder(sender, instance, created, **kwargs):
        if created and (sender == RotationControlAdvertiserFolder or sender == RotationControlAdvertiserSplit):
            CapFolder.objects.create(parent=instance, name='CAP')

    def select_advertiser(self):
        capfolder: CapFolder = self.get_cap()
        if capfolder.is_full():
            raise AdvertiserCapIsFull(
                f'Advertiser cap is full #{capfolder.id}')
        elif not capfolder:
            raise AdvertiserCapNotExist(
                f'Advertiser cap does not exist #{capfolder.id}')
        return self

    def get_cap(self):
        # TODO: might casue problems, need to fix this
        return self.get_descendants(include_self=False).instance_of(CapFolder).first()

    def push(self, lead) -> bool:
        # push lead to advertiser
        # return True if success otherwise return False
        capfolder: CapFolder = self.get_cap()
        if not capfolder:
            raise RotationControlAdvertiserFolder(
                f'Advertiser folder {self.id} does not have a cap folder')

        if capfolder.is_full():
            raise AdvertiserCapIsFull(
                f'Advertiser cap is full #{capfolder.id}')

        self.advertiser: Advertiser
        success = self.advertiser.push_lead(lead)
        self.fill(success)
        return success

    def fill(self, success: bool):
        capfolder: CapFolder = self.get_cap()
        if not capfolder:
            raise CapFolderDoesNotExist(
                f'Advertiser folder {self.id} does not have a cap folder')

        capfolder.fill(success=success)

    def pass_rule(self, **kwargs):
        # pass rule if cap is not full
        return True


class RotationControlAdvertiserSplit(RotationControl, AdvertiserFolder):
    weight = models.IntegerField(default=0)
    fill_first = models.BooleanField(default=False)
    counter_updated = models.DateTimeField(auto_now=True)

    @ property
    def percentage(self):
        if not self.weight or not self.parent.total_weight or not self.is_active or not self.children.filter(is_active=True).exists():
            return 0
        cent = self.weight / self.parent.total_weight
        # return 2 deciml points
        return round(cent * 100, 2)

    @ property
    def icon(self):
        return 'https://foxesmedia-ld.platform500.com/assets/img/rotation-trees/ico/A.svg'

    class Meta:
        verbose_name = 'Advertiser Split'
        verbose_name_plural = 'Advertiser Split'

    def clean(self):
        # check if parent is not null, and self is type of SplitFolder
        if not isinstance(self.parent, SplitFolder):
            raise ValidationError(
                'Advertiser Split parent must be of type SplitFolder')


class RotationControlAffiliateSplitFolder(SplitFolder, TargetFolder, AffiliateFolder):
    class Meta:
        verbose_name = 'Affiliate Split Folder'
        verbose_name_plural = 'Affiliate Split Folders'

    child_types = [
        RotationControlAdvertiserSplit,
    ]


class RotationControlCountrySplitFolder(SplitFolder, TargetFolder, CountryFolder):
    class Meta:
        verbose_name = 'Country Split Folder'
        verbose_name_plural = 'Country Split Folders'

    child_types = [
        RotationControlAdvertiserSplit,
    ]
