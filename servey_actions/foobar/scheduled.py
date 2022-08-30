from servey.action import action
from servey.trigger.fixed_rate_trigger import FixedRateTrigger


#@action(triggers=(FixedRateTrigger(5),))
def ping() -> type(None):
    print("PING")
