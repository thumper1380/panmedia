# services.py

from apps.trafficdata.models import TrafficData
from apps.traffic_distribution.rotation_control.service import RotationControlService
from apps.traffic_distribution.queue_management.service import QueueManagementService


class LeadService:
    def __init__(self, lead: TrafficData):
        self.lead = lead

    def process(self):
        return QueueManagementService(self.lead).handle() | RotationControlService(self.lead).handle()
