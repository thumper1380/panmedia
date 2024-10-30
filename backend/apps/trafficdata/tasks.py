
from requests import request, HTTPError
from requests.exceptions import ConnectionError, Timeout
from django.template import Template, Context
from celery import shared_task
from django.core.cache import cache
from django.db import transaction
from django.apps import apps
from .states import PostbackStatusChoices
from apps.traffic_distribution.exceptions import AdvertiserRejectedException, RotationDoesNotExist
from .states import QueueLeadStatusChoices

LOCK_EXPIRE = 60 * 5  # Lock expires in 5 minutes


@shared_task(bind=True, name='queue_lead')
def queue_lead(self, lead_id):
    with transaction.atomic():  # start a new transaction
        # Lock the lead for update
        TrafficData = apps.get_model('trafficdata', 'TrafficData')
        QueueLead = apps.get_model('trafficdata', 'QueueLead')
        RotationControl = apps.get_model('traffic_distribution', 'RotationControl')

        lead = TrafficData.objects.select_for_update().get(pk=lead_id)
        lead.info(f'adding lead #{lead.id} to queue')
        q_lead = lead.queue

        # If you want to ensure that only one task can run at a time across all workers,
        # You can use self.request.id to lock the task execution across all workers.
        lock_id = f'queue_lead-{self.request.id}'
        acquire_lock = cache.add(lock_id, "true", LOCK_EXPIRE)
        if acquire_lock:
            # set status to success
            caps = RotationControl.search(
                affiliate_id=lead.affiliate.id, country=lead.country)
            try:
                cap_folder, advertiser_lead_id, auto_login = caps.send(lead)
            except AdvertiserRejectedException as e:
                q_lead.set_status(QueueLeadStatusChoices.FAILED)
                return f'Advertiser rejected lead #{lead.id} with reason: {e}'
            except RotationDoesNotExist as e:
                q_lead.set_status(QueueLeadStatusChoices.FAILED)
                return 'No rotation found for this lead.'

            advertiserfolder = cap_folder.parent
            message = f'Pushed lead #{lead.id} from queue to advertiser {advertiserfolder.advertiser.name} / #{advertiserfolder.id} CAP #{cap_folder.id}'
            lead.advertiser_accepted(
                description=message,
                advertiser_external_id=advertiser_lead_id,
                advertiser_id=advertiserfolder.advertiser.id,
                auto_login_url=auto_login,
            )
            lead.save()
            q_lead.set_status(QueueLeadStatusChoices.SUCCESS)
            return message
        else:
            # task is already running
            raise self.retry(countdown=5, max_retries=3)


@shared_task(bind=True)
def fire_executed_postback(self, executed_postback_id):
    task_id = self.request.id
    TrafficData = apps.get_model('trafficdata', 'TrafficData')
    ExecutedPostback = apps.get_model('trafficdata', 'ExecutedPostback')

    executed_postback = ExecutedPostback.objects.get(id=executed_postback_id)
    lead_id = executed_postback.trafficdata.id
    lead = TrafficData.objects.get(id=lead_id)
    lead_serialized = lead.get_serialized_data()
    method = executed_postback.method
    content = executed_postback.content
    template = Template(content)
    rendered_content = template.render(Context(lead_serialized))
    try:
        res = request(method, rendered_content)
        status = PostbackStatusChoices.SUCCESS if res.ok else PostbackStatusChoices.ERROR
        executed_postback.status = status
        executed_postback.task_id = task_id
        executed_postback.message = res.text
        executed_postback.save()
        return res.status_code
    except HTTPError as errh:
        executed_postback.status = PostbackStatusChoices.ERROR
        executed_postback.message = str(errh)
        executed_postback.task_id = task_id
        executed_postback.save()
        return errh.response.status_code
    except ConnectionError as errc:
        executed_postback.status = PostbackStatusChoices.ERROR
        executed_postback.message = str(errc)
        executed_postback.task_id = task_id
        executed_postback.save()
        return errc.response.status_code
    except Timeout as errt:
        executed_postback.status = PostbackStatusChoices.ERROR
        executed_postback.message = str(errt)
        executed_postback.task_id = task_id
        executed_postback.save()
        return errt.response.status_code
