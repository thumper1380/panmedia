from common.service import ServiceBase
from .models import QueueManagement
from apps.trafficdata.models import TrafficData
from .exceptions import QueueNotFound
from .manager import QueueManagementManager


class QueueManagementService(ServiceBase):
    def __init__(self, lead: TrafficData):
        self.lead = lead

    def add_to_queue(self):
        # method to add lead to queue
        try:
            queue_management = QueueManagement.objects.get_queue(
                country=self.country)

            if queue_management.should_get_in_queue() and not queue_management.is_within_working_hours():
                message = f'Lead {self.id} added to queue #{queue_management.id}'
                self.queue_lead(
                    description=message,
                    eta=queue_management.next_working_hour(),
                    queue=queue_management
                )
                thank_you_url = queue_management.get_thank_you_url()
                self.set_auto_login_url(thank_you_url)
                self.save()
                return True
        except QueueManagement.DoesNotExist:
            pass
        except QueueNotFound as e:
            pass
        except Exception as e:
            self.error(f'Queue management error: {e}')
            raise e

    def handle(self):
        self.add_to_queue()
