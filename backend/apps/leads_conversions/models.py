from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.db import models
from djmoney.models.fields import MoneyField, Money
# Create your models here.

#import mptt
from polymorphic_tree.models import PolymorphicMPTTModel
from polymorphic_tree.managers import PolymorphicMPTTModelManager, PolymorphicMPTTQuerySet
#import TreeForeignKey

from apps.utils.folders import Folder, AffiliateFolder, AdvertiserFolder, CountryFolder, TargetFolder, FolderManager




class PayoutsQuerySet(FolderManager, PolymorphicMPTTQuerySet):
    ...


class Payouts(Folder):
    """Model definition for Payouts."""
    objects = PayoutsQuerySet.as_manager()

    class Meta:
        verbose_name = _("Payouts")
        verbose_name_plural = _("Payouts")

    def __str__(self):
        return self.name


class PayoutAffiliateFolder(Payouts, AffiliateFolder):
    ...


class PayoutCountryFolder(Payouts, CountryFolder):
    ...


class PayoutAdvertiserFolder(Payouts, AdvertiserFolder):
    ...


class PayoutFolder(TargetFolder, Payouts):
    value = MoneyField(max_digits=14, decimal_places=2,
                       default=Money("0", "USD"))

    class Meta:
        verbose_name = _("Payout")
        verbose_name_plural = _("Payouts")


class RevenuesQuerySet(FolderManager, PolymorphicMPTTQuerySet):
    ...


class Revenues(Folder):
    objects = RevenuesQuerySet.as_manager()

    class Meta:
        verbose_name = _("Revenue")
        verbose_name_plural = _("Revenues")


class RevenueAffiliateFolder(Revenues, AffiliateFolder):
    ...


class RevenueCountryFolder(Revenues, CountryFolder):
    ...


class RevenueAdvertiserFolder(Revenues, AdvertiserFolder):
    ...


class RevenueFolder(TargetFolder, Revenues):
    value = MoneyField(max_digits=14, decimal_places=2,
                       default=Money("0", "USD"))

    class Meta:
        verbose_name = _("Revenue Folder")
        verbose_name_plural = _("Revenue Folders")
