from .models import RotationControl
from common.service import ServiceBase

from apps.trafficdata.models import TrafficData, PushingAttemptLog, PushingErrorLog
from .exceptions import PushLeadException, AdvertiserRejectedException, RotationDoesNotExist


class RotationControlService(ServiceBase):
    def __init__(self, lead: TrafficData):
        self.lead = lead

    def push(self):
        caps = RotationControl.search(
            affiliate_id=self.lead.lead.affiliate.id, country=self.lead.lead.country)
        if not caps.exists():
            self.lead.debug(
                f'Rotation does not exist: There is no active rotation for this affiliate {self.lead.affiliate} / #{self.lead.affiliate.id}')
            self.lead.advertisers_declined(
                description=f'There is no active rotation for this affiliate {self.lead.affiliate.company_name} / #{self.lead.affiliate.id}')
            self.lead.save()
            raise PushLeadException(
                f'There is no active rotation for this affiliate {self.lead.affiliate.company_name} / #{self.lead.affiliate.id}')

        try:
            cap_folder, advertiser_lead_id, auto_login = caps.send(self.lead)
        except RotationDoesNotExist as e:
            PushingErrorLog.objects.create(
                trafficdata=self.lead,
                message=e
            )
            raise PushLeadException(e)
        except AdvertiserRejectedException as e:
            raise PushLeadException(e)

        message = 'Log after pushing:\n'
        for i, cap in enumerate(caps):
            message += f'{i+1}. {cap.advertiser.name} #{cap.advertiser.id} CAP #{cap.id}\n\n'

        # add Registered to: advertiser name
        message += f'>> Registered to: {cap_folder.advertiser.name} #{cap_folder.advertiser.id}'

        PushingAttemptLog.objects.create(
            trafficdata=self.lead,
            message=message,
        )

        advertiserfolder = cap_folder.parent
        message = f'Lead {self.lead.id} pushed to advertiser {advertiserfolder.advertiser} #{advertiserfolder.id} CAP #{cap_folder.id}'
        self.lead.advertiser_accepted(
            description=message,
            advertiser_external_id=advertiser_lead_id,
            advertiser_id=advertiserfolder.advertiser.id,
            auto_login_url=auto_login,
        )
        self.lead.save()

        return True

    def handle(self):
        self.push()
        return True
