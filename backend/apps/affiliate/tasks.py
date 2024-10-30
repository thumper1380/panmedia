from celery import shared_task
from django.template import Template, Context
from requests import request
from django.apps import apps
from django.db import transaction


@shared_task(bind=True)
def schedule_fire(self, lead_id, content, method):
    with transaction.atomic():
        TrafficData = apps.get_model('trafficdata', 'TrafficData')
        task_id = self.request.id
        lead = TrafficData.objects.select_for_update().get(pk=lead_id)

        lead_serialized = lead.get_serialized_data()
        template = Template(content)
        rendered_content = template.render(Context(lead_serialized))
        try:
            res = request(method, rendered_content)
            status = 'success' if res.ok else 'error'
            message = res.text
        except Exception as e:
            status = 'error'
            message = str(e)
        finally:
            lead.executed_postbacks.create(
                task_id=task_id,
                status=status,
                content=rendered_content,
                message=message
            )