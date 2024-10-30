from common.folders.models import Folder, TargetFolder, CountryFolder, AffiliateFolder
from .exceptions import CapIsFull
from django.db import models
from django.utils.translation import gettext_lazy as _


class CapFolder(TargetFolder):
    class Meta:
        verbose_name = _("Cap Folder")
        verbose_name_plural = _("Cap Folders")


class RotationControl(Folder):
    class Meta:
        verbose_name = _("Rotation Control")
        verbose_name_plural = _("Rotation Control")

    can_have_siblings = False
    can_be_root = True
    
    
    
    child_types = [
        CountryFolder,
        AffiliateFolder,
        CapFolder
    ]
    
    
    def search(self, **kwargs):
        return self.tree(folder=self, **kwargs)