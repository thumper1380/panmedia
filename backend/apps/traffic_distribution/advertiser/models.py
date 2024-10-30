from django.db import models
from django.db.models import Q
import random

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
        raise exepction(ADVERTISER_REJECT_MESSAGE.format(advertiser_name=self.name, advertiser_id=self.id) + message)

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