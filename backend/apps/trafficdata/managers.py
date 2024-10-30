from django.db import models
from .states import PostbackStatusChoices
from config.celery import app
from .states import QueueLeadStatusChoices, StateChoices
from djmoney.money import Money
from django.db.models import Sum, Q, F
import jwt
from django.conf import settings
from .exceptions import InvalidToken, InvalidSecret
from apps.settings.models import CRMSettings
from django.utils import timezone, dateparse
from datetime import timedelta

class ExecutedPostbackQuerySet(models.QuerySet):
    def fire(self):
        pending_postbacks = self.filter(status=PostbackStatusChoices.PENDING)
        for postback in pending_postbacks:
            postback.fire()


class TrafficDataQuerySet(models.QuerySet):
    def clicks(self):
        return self.filter(Q(state=StateChoices.CLICK) | Q(state=StateChoices.CLICK_LANDED))

    def leads(self):
        return self.filter(Q(state=StateChoices.LEAD) | Q(state=StateChoices.LEAD_QUEUED) | Q(state=StateChoices.LEAD_PUSHED) | Q(state=StateChoices.LEAD_DECLINED))

    def sales(self):
        return self.filter(state=StateChoices.SALE)

    def queue(self):
        return self.filter(state=StateChoices.LEAD_QUEUED)

    def get_by_jwt_token(self, jwt_token: str, **kwargs):
        """
        Retrieves a TrafficData object by decoding a JWT token.

        Args:
            jwt_token (str): The JWT token to decode.
            **kwargs: Additional keyword arguments to pass to the `get` method.

        Returns:
            TrafficData: The TrafficData object associated with the decoded token.

        Raises:
            InvalidToken: If the token is invalid or has expired.
            self.model.DoesNotExist: If the TrafficData object does not exist.
            InvalidSecret: If the secret in the token does not match the TrafficData object's secret.
        """
        try:
            decoded_data = jwt.decode(
                jwt_token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.exceptions.DecodeError:
            raise InvalidToken('Invalid token')

        lead_id = decoded_data['i']
        lead_secret = decoded_data['s']
        token_created_at = decoded_data['t']  # timestamp
        # check if token is expired
        token_ttl = CRMSettings.load().token_ttl  # ttl in hours
        if token_created_at + token_ttl * 60 * 60 < timezone.now().timestamp():
            raise InvalidToken('Token expired')

        try:
            trafficdata = self.get(id=lead_id)
        except self.model.DoesNotExist:
            raise self.model.DoesNotExist('Lead does not exist')
        if trafficdata.secret != lead_secret:
            raise InvalidSecret('Invalid secret')

        return trafficdata
    
    # def filter(self, *args, **kwargs):
    #     # Map keyword arguments to their corresponding keys in the profile JSONField
    #     model_fields = [f.name for f in self.model._meta.get_fields()]
    #     reserved_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    #     profile_args = {
    #         f'profile__{k}': v for k, v in kwargs.items() if k not in model_fields + reserved_fields}

    #     other_args = {k: v for k, v in kwargs.items(
    #     ) if k in profile_args.keys() or k in model_fields}
    #     return super().filter(*args, **other_args, **profile_args)


    def late_conversions(self):
        # late conversions are conversions that were created after 24 hours of the click
        return self.filter(conversions__created_at__gte=F('created_at') + timedelta(hours=24))


    
class TrafficDataManager(models.Manager):
    def get_queryset(self):
        return TrafficDataQuerySet(self.model, using=self._db)

    def get_by_jwt_token(self, jwt_token: str, **kwargs):
        return self.get_queryset().get_by_jwt_token(jwt_token, **kwargs)

    def filter(self, *args, **kwargs):
        return self.get_queryset().filter(*args, **kwargs)
    
    def late_conversions(self):
        return self.get_queryset().late_conversions()
    



class QueueLeadQuerySet(models.QuerySet):
    def revoke(self, delete=False, *args, **kwargs):
        task_ids = list(self.filter(status=QueueLeadStatusChoices.PENDING,
                        **kwargs).values_list('task_id', flat=True))
        app.control.revoke(task_ids, terminate=True)
        self.filter(status=QueueLeadStatusChoices.PENDING).update(status=QueueLeadStatusChoices.REVOKED, task_id=None, time=None)
        if delete:
            self.filter(**kwargs).delete()


class ClickManager(TrafficDataManager):
    def get_queryset(self):
        return super(ClickManager, self).get_queryset().clicks()


class LeadManager(TrafficDataManager):
    def get_queryset(self):
        return super(LeadManager, self).get_queryset().leads()


class SaleManager(TrafficDataManager):
    def get_queryset(self):
        return super(SaleManager, self).get_queryset().sales()


class ConversionQuerySet(models.QuerySet):
    def payout(self) -> Money:
        payout = self.aggregate(payout=Sum('payout'))['payout']
        return Money(payout, 'USD') if payout else Money(0, 'USD')

    def revenue(self) -> Money:
        revenue = self.aggregate(revenue=Sum('revenue'))['revenue']
        return Money(revenue, 'USD') if revenue else Money(0, 'USD')

    def sale_status(self):
        latest_conversion = self.order_by('-created_at').first()
        return latest_conversion.goal.force_sale_status if latest_conversion else None


class AffiliateClickManager(ClickManager):
    def get_queryset(self):
        return super(AffiliateClickManager, self).get_queryset().filter(affiliate__isnull=False, is_risky=False)


class AffiliateLeadManager(LeadManager):
    def get_queryset(self):
        return super(AffiliateLeadManager, self).get_queryset().filter(affiliate__isnull=False, is_risky=False)


class AffiliateSaleManager(SaleManager):
    def get_queryset(self):
        return super(AffiliateSaleManager, self).get_queryset().filter(affiliate__isnull=False, is_risky=False)
