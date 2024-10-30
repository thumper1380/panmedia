from functools import wraps
from django_fsm import transition
from .states import TrafficDataLogTypeChoices

def logged_transition(*args, **kwargs):
    from .models import StateSwitchedLog, StateInitiatedLog
    target = kwargs.get('target')
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            instance = args[0]
            state = instance.state
            if state:
                StateSwitchedLog.objects.create(trafficdata=instance, source_state=state, target_state=target)
            else :
                StateInitiatedLog.objects.create(trafficdata=instance, initial_state=target)
            return func(*args, **kwargs)
        return transition(*args, **kwargs)(wrapper)
    return decorator
