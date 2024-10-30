from django.db.models.signals import post_save
from .models import Assigned, Unassigned
from django.dispatch import receiver
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import GroupTemplate, APIConnection, Settings, Provider


# @receiver(post_migrate)
# def create_options(sender, **kwargs):
#     PasswordRule.objects.get_or_create(rule=RuleChoices.UPPERCASE_LETTERS)
#     PasswordRule.objects.get_or_create(rule=RuleChoices.LOWERCASE_LETTERS)
#     PasswordRule.objects.get_or_create(rule=RuleChoices.NUMBERS)
#     PasswordRule.objects.get_or_create(rule=RuleChoices.SPECIAL_CHARACTERS)


@receiver(post_save, sender=Assigned)
def remove_unassigned(sender, instance, **kwargs):
    Unassigned.objects.filter(label=instance.label, advertiser=instance.sale_status_mapping.advertiser).delete()






def update_advertiser_fields(instance, **kwargs):
    print('update_advertiser_fields')
    def _update_advertisers():
        # instance is the GroupTemplate that just got saved
        provider = instance.provider
        # Iterate over all advertisers of this provider
        for advertiser in provider.advertiser_set.all():
            # Check if this group template is already associated with the advertiser
            api_connection = advertiser.apiconnection_set.filter(
                group_template=instance).first()
            if not api_connection:
                # If not, create a new APIConnection
                api_connection = APIConnection.objects.create(
                    advertiser=advertiser, group_template=instance)
            # Get a list of current settings for this API connection
            current_settings_templates = set(
                api_connection.settings_set.values_list('template_id', flat=True))
            # Get a list of all settings templates from current group template
            group_settings_templates = set(
                instance.settingstemplate_set.values_list('id', flat=True))
            # Find settings templates which have been removed in the current group template
            removed_settings_templates = current_settings_templates - group_settings_templates
            # Delete settings corresponding to removed settings templates
            api_connection.settings_set.filter(
                template_id__in=removed_settings_templates).delete()
            # Find new settings templates added in the current group template
            new_settings_templates = group_settings_templates - current_settings_templates
            # Add new settings based on new settings templates
            for new_settings_template_id in new_settings_templates:
                Settings.objects.create(
                    api_connection=api_connection, template_id=new_settings_template_id)

    transaction.on_commit(_update_advertisers)

from .models import Advertiser
@receiver(post_save, sender=Advertiser)
def update_after_saving_advertiser(sender, instance, **kwargs):
    provider = instance.provider
    group_templates = provider.grouptemplate_set.all()
    for group_template in group_templates:
        update_advertiser_fields(group_template, **kwargs)


@receiver(post_save, sender=Provider)
def update_after_saving_provider(sender, instance, **kwargs):
    group_templates = instance.grouptemplate_set.all()
    for group_template in group_templates:
        update_advertiser_fields(group_template, **kwargs)