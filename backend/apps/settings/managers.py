
from .models import Event, EventLog
from django.db import models
# import polymorphicmptt
from polymorphic_tree.managers import PolymorphicMPTTQuerySet
from apps.utils.folders import ManagementManager

class CRMTermQuerySet(models.QuerySet):
    def calculate(self, context):
        for term in self:
            context[term.label] = term.calculate_value(context)
        return context


class RiskManagementQuerySet(PolymorphicMPTTQuerySet, ManagementManager):
    ...


class SMSManagementQuerySet(PolymorphicMPTTQuerySet, ManagementManager):
    ...


class QueueManagementManager(models.Manager):
    def get_queue(self, country):
        try:
            return self.get(country=country, is_enabled=True)
        except self.model.DoesNotExist:
            raise self.model.DoesNotExist.QueueManagementException(
                f'Queue for {country} does not exist')





class EventLogManager(models.Manager):
    def create_event_log(self, event, trafficdata):
        if isinstance(event, str):
            event_name = event
            event = Event.objects.get(name=event_name)

        if isinstance(trafficdata, int) or isinstance(trafficdata, str):
            from apps.trafficdata.models import TrafficData
            trafficdata_id = trafficdata
            trafficdata = TrafficData.objects.get(id=trafficdata_id)

        is_unique = event.is_unique
        if is_unique:
            event_logs = EventLog.objects.filter(
                event=event, trafficdata=trafficdata)
            if event_logs.exists():
                return event_logs.first()

        event_log = EventLog.objects.create(
            event=event, trafficdata=trafficdata)
        return event_log
