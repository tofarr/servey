from typing import Optional

from marshy.types import ExternalItemType

from servey.action_meta import ActionMeta
from servey.integration.aws.serverless_event_factory.serverless_event_factory_abc import ServerlessEventFactoryABC
from servey.trigger.fixed_rate_trigger import FixedRateTrigger


class FixedRateEventFactory(ServerlessEventFactoryABC):

    def create_event(self, action_meta: ActionMeta) -> Optional[ExternalItemType]:
        trigger = next((t for t in action_meta.triggers if isinstance(t, FixedRateTrigger)), None)
        if not trigger:
            return
        result = {
            'schedule': {
                'rate': f'rate({trigger.interval} seconds)'
            }
        }
        return result
