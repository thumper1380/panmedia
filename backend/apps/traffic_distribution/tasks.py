from celery.exceptions import MaxRetriesExceededError
from django.db import transaction
from django.core.cache import cache
from datetime import timedelta
from celery import shared_task
from django.apps import apps

LOCK_EXPIRE = 60 * 5  # Lock expires in 5 minutes


@shared_task
def pull_advertiser_leads_statuses(advertiser_id):
    # Advertiser = apps.get_model('traffic_distribution', 'Advertiser')
    from apps.traffic_distribution.models import Advertiser

    advertiser: Advertiser = Advertiser.objects.get(pk=advertiser_id)
    leads_status = advertiser.pull_leads()
    if not leads_status:
        return

    leads_status = leads_status.json()

    leads = advertiser.leads()
    for lead in leads:
        status = next((item for item in leads_status if str(
            item["advertiser_external_id"]) == lead.advertiser_external_id), None)
        if status:
            lead.update_status(status['sale_status'])
            lead.save()

    # advertiser.info(f'Pulling leads statuses for advertiser {advertiser.name}, {len(leads_status)} statuses pulled')
    return f'Leads statuses pulled for advertiser {advertiser.name}'


@shared_task
def pull_leads_statuses():
    # Advertiser = apps.get_model('traffic_distribution', 'Advertiser')
    from apps.traffic_distribution.models import Advertiser
    # retrieve all advertisers
    advertisers = Advertiser.objects.filter(is_test=False)
    # pull the leads statuses for each advertiser
    for advertiser in advertisers:
        pull_advertiser_leads_statuses.delay(advertiser.id)


@shared_task
def pull_advertiser_convertions(advertiser_id):
    # Advertiser = apps.get_model('traffic_distribution', 'Advertiser')
    from apps.traffic_distribution.models import Advertiser

    advertiser = Advertiser.objects.get(pk=advertiser_id)

    conversions = advertiser.pull_conversions()
    if not conversions:
        return

    conversions = conversions.json()
    leads = advertiser.leads().filter(advertiser_external_id__in=conversions)
    for lead in leads:
        lead.advertiser_ftd_event()
        lead.save()
    # advertiser.info(f'Pulling conversions for advertiser {advertiser.name}, {len(conversions)} conversions pulled')
    return f'{len(conversions)} conversions pulled from advertiser {advertiser.name}'


@shared_task
def pull_conversions():
    # Advertiser = apps.get_model('traffic_distribution', 'Advertiser')
    from apps.traffic_distribution.models import Advertiser
    # retrieve all advertisers
    advertisers = Advertiser.objects.filter(is_test=False)
    # pull the leads statuses for each advertiser
    for advertiser in advertisers:
        pull_advertiser_convertions.delay(advertiser.id)


@shared_task
def reset_caps():
    # RotationControl = apps.get_model('traffic_distribution', 'RotationControl')
    from apps.traffic_distribution.models import RotationControl

    RotationControl.reset_caps()


@shared_task(bind=True, max_retries=3)
def rejected_handler(self, lead_id):
    # Generate a unique cache key for this task
    lock_key = f'push_rejected:{lead_id}'

    # Attempt to acquire the lock
    def acquire_lock(): return cache.add(lock_key, 'lock', LOCK_EXPIRE)
    def release_lock(): return cache.delete(lock_key)
    if acquire_lock():
        try:
            with transaction.atomic():
                # TrafficData = apps.get_model('trafficdata', 'TrafficData')
                from apps.trafficdata.models import TrafficData
                
                lead: TrafficData = TrafficData.objects.select_for_update().get(pk=lead_id)
                if lead.retry_count >= 10:
                    return f'Lead {lead.id} has reached max retries'

                lead.try_again(
                    description='Trying to push lead again. Attempt #{}'.format(
                        lead.retry_count + 1),
                )
                lead.save()
                try:
                    success = lead.push_brands()
                    return f'Lead pushed successfully to brands #{lead.id}'
                except Exception as e:
                    lead.retry_count += 1
                    lead.save()
                    release_lock()
                    return f'Failed to push lead to brands #{lead.id}. attempt #{lead.retry_count}'
        except MaxRetriesExceededError as e:
            # Max retries exceeded, release the lock and re-raise the exception
            release_lock()
            raise e
    else:
        # The lock is already acquired by another task
        # Retry the task after a delay
        raise self.retry(countdown=timedelta(seconds=10).total_seconds())
