from django.db import models
from polymorphic_tree.models import PolymorphicMPTTModel, PolymorphicTreeForeignKey, ValidationError
from django_countries.fields import CountryField
from apps.affiliate.models import Affiliate
from apps.traffic_distribution.models import Advertiser
from polymorphic_tree.managers import PolymorphicMPTTModelManager


class FolderManager(PolymorphicMPTTModelManager):
    def set_active(self, is_active: bool, include_self=True):
        if include_self:
            self.get_queryset().update(is_active=is_active)
        else:
            self.get_queryset().exclude(pk=self.pk).update(is_active=is_active)


class Folder(PolymorphicMPTTModel):
    name = models.CharField(max_length=255)
    parent = PolymorphicTreeForeignKey(
        'self', null=True, blank=True, related_name='children', db_index=True, on_delete=models.CASCADE)
    is_active = models.BooleanField(verbose_name='Active', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = FolderManager()

    class Meta:
        abstract = True

    can_have_siblings = True
    can_be_root = False

    def set_active(self, is_active: bool, set_children=False):
        self.is_active = is_active
        self.save()
        if set_children:
            self.get_children().update(is_active=is_active)

    def delete(self, using=None, keep_parents=True):
        return super().delete(using=using, keep_parents=keep_parents)

    def get_children(self, **kwargs):
        return super().get_children().filter(**kwargs)

    def get_descendants(self, include_self=False):
        return super().get_descendants(include_self=include_self).filter()

    def get_family(self):
        root = self.get_root()
        return root.get_descendants(include_self=True)

    def clean(self):
        super().clean()
        if not self.can_have_siblings:
            if self.parent and self.parent.children.exists() and self.pk is None:
                raise ValidationError(
                    {self._mptt_meta.parent_attr: 'Folder can not have siblings'})

    def tree(self, folder: 'Folder', **kwargs) -> 'TargetFolder':
        if isinstance(folder, TargetFolder):
            return folder
        for child in folder.get_children():
            if child.pass_rule(**kwargs):
                return self.tree(folder=child, **kwargs)

    def __str__(self):
        return self.name

    @property
    def icon(self):
        return 'https://foxesmedia-ld.platform500.com/assets/img/rotation-trees/ico/RB.svg'

    def pass_rule(self, **kwargs):
        return True


class CountryFolder(Folder):
    countries = CountryField(multiple=True)

    def pass_rule(self, **kwargs):
        if 'country' in kwargs:
            return kwargs['country'] in self.countries
        return False


class AffiliateFolder(Folder):
    affiliate = models.ForeignKey(Affiliate, on_delete=models.CASCADE)

    def pass_rule(self, **kwargs):
        if 'affiliate_id' in kwargs:
            return self.affiliate.id == kwargs['affiliate_id']
        return False


class AdvertiserFolder(Folder):
    advertiser = models.ForeignKey(Advertiser, on_delete=models.CASCADE)

    def pass_rule(self, **kwargs):
        if 'advertiser_id' in kwargs:
            return self.advertiser.id == kwargs['advertiser_id']
        return False


class TargetFolder:
    can_have_children = False
    can_be_root = False
    can_have_siblings = False
