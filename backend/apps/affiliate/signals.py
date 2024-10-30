from django.dispatch import receiver
from django_fsm.signals import post_transition
from apps.trafficdata.models import TrafficData


@receiver(post_transition)
def notify_(sender, instance: TrafficData, **kwargs):
    print('post_transition!!', sender)
    trafficdata = instance
    state = kwargs['target']
    if not trafficdata.is_risky:
        affiliate = trafficdata.affiliate
        trafficdata_serialized = instance.get_serialized_data()
        affiliate.notify_telegram(state, **trafficdata_serialized)
        affiliate.postbacks.fire(goal=state, lead=trafficdata)
    else:
        trafficdata.affiliate.postbacks.pending(goal=state, lead=trafficdata)
