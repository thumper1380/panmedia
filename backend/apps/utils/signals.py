from django_fsm.signals import pre_transition
from django.dispatch import receiver
from apps.utils.folders import Management



@receiver(pre_transition)
def run(sender, instance, **kwargs):
    print('Management signal received')
    for _class in Management.__subclasses__():
        trafficdata = instance

        traffic_data_serializer = trafficdata.get_serialized_data()
        folder = _class.search(
            **{**traffic_data_serializer, **kwargs})
        # print(folder)
        if folder:
            folder.execute(instance, **kwargs)
