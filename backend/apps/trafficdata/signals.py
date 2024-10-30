from .tasks import queue_lead
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_fsm.signals import pre_transition, post_transition
from .models import TrafficData, QueueLead, Lead, Conversion, AdvertiserSaleStatus

# on transition check offer or advertiser goal and create conversion


@receiver(pre_transition)
def create_conversion(sender, instance, name, source, target, **kwargs):
    # if funnel goal is reached create conversion
    if sender == TrafficData or sender == Lead:
        print('post_transition', name, source, target)
        if instance.advertiser:
            goal = instance.advertiser.get_goal()
            print('goal', goal)
            print(type(goal))
            if target == goal.state:
                print('goal reached')
                payout = instance.get_payout()
                revenue = instance.get_revenue()
                Conversion.objects.create(
                    trafficdata=instance,
                    revenue=revenue,
                    payout=payout,
                    goal=goal,
                )


@receiver(post_transition)
def update_afm_state(sender, instance, name, source, target, **kwargs):
    if getattr(instance, '_updating', False):  # Check if already updating
        return
    print('Trying to update afm state')
    if not instance.is_risky:
        instance._updating = True  # Set flag
        
        print('update_afm_state', instance.advertiser_sale_status)
        print('update_afm_state', instance.state)

        instance.afm_state = instance.state  # TODO: Fix this
        instance.afm_status = instance.advertiser_sale_status  # TODO: Fix this
        
        instance.save(update_fields=['afm_state', 'afm_status'])
        instance._updating = False  # Reset flag
        
        



@receiver(post_save, sender=QueueLead)
def queue_lead_signal(sender, instance, created, **kwargs):
    if created:
        eta = instance.time
        task = queue_lead.apply_async(args=[instance.trafficdata.id], eta=eta)
        sender.objects.filter(id=instance.id).update(task_id=task.id)
