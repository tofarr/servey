from abc import ABC, abstractmethod

from marshy.types import ExternalItemType

from servey.action.action_meta import ActionMeta
from servey.action.trigger.trigger_abc import TriggerABC


class TriggerHandlerABC(ABC):
    @abstractmethod
    def handle_trigger(
        self,
        action_meta: ActionMeta,
        trigger: TriggerABC,
        lambda_definition: ExternalItemType,
    ):
        """Add definitions for the trigger given to the lambda_definition"""
