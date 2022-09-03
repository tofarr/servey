from marshy.types import ExternalItemType

from servey.trigger.trigger_abc import TriggerABC
from servey2.action.action_meta import ActionMeta
from servey2.action.trigger.fixed_rate_trigger import FixedRateTrigger
from servey2.servey_aws.serverless.trigger_handler.trigger_handler_abc import TriggerHandlerABC


UNITS = {
    'days': 86400,
    'hours': 3600,
    'minutes': 60
}


class FixedRateTriggerHandler(TriggerHandlerABC):

    def handle_trigger(self, action_meta: ActionMeta, trigger: TriggerABC, lambda_definition: ExternalItemType):
        if not isinstance(trigger, FixedRateTrigger):
            return
        events = lambda_definition.get('events')
        if not events:
            events = lambda_definition['events'] = {}
        for unit, seconds in UNITS:
            if not trigger.interval % seconds:
                events['schedule'] = dict(rate=f"rate({trigger.interval / seconds} {unit})")
                return
        events['schedule'] = dict(rate=f"rate({trigger.interval} seconds)")
