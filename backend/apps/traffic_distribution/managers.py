# from .models import Response
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import F
from .exceptions import AdvertiserCapIsFull, AdvertiserCapNotExist, AdvertiserRejectedException, ResponseException, RotationDoesNotExist, RotationStractureIsNotValid
from .tasks import rejected_handler
from polymorphic_tree.managers import PolymorphicMPTTQuerySet
from polymorphic.managers import PolymorphicQuerySet


class GroupQuerySet(models.QuerySet):
    def get_all_settings(self):
        for group in self:
            yield group.get_all_settings()



class SettingsTemplateQuerySet(models.QuerySet):
    ...


class ResponseQuerySet(PolymorphicQuerySet):
    def get_response(self, response):
        _response = self.filter(status_code=response.status_code)

        if not _response.exists():
            # raise Response(response=response, caller=response.request.headers.get('class'), status_code=response.status_code)
            _response = self.model()
            _response.status_code = response.status_code
            _response.caller = response.request.headers.get('class')
            _response.response = response
            return _response

        _response = _response.first()
        _response.response = response
        _response.caller = response.request.headers.get('class')

        return _response



class RotationControlQuerySet(PolymorphicMPTTQuerySet):
    ...


class CapFolderQuerySet(PolymorphicMPTTQuerySet):
    def reset(self):
        return self.update(current_amount=0)

    def send(self, lead, **kwargs):
        for cap_folder in self:
            try:
                response = cap_folder.send_lead_to_advertiser(lead)
                cap_folder.fill()
                return response

            except AdvertiserRejectedException as e:  # advertiser rejected lead
                cap_folder.fill(False)
                message = e
                from apps.trafficdata.models import PushingErrorLog
                PushingErrorLog.objects.create(trafficdata=lead, message=message)
                

        lead.advertisers_declined(description=message)
        lead.save()
        # print all caps in this format: Advertiser #{advertiser.id} Cap #{cap.id}
        rejected_handler.apply_async((lead.id,), countdown=60)
        raise AdvertiserRejectedException(message)


class AdvertiserFolderQuerySet(PolymorphicMPTTQuerySet):
    ...


class SplitFolderQuerySet(PolymorphicMPTTQuerySet):
    ...