from marshy.types import ExternalItemType

from servey.action.action import Action
from servey.trigger.trigger_abc import TriggerABC
from servey.trigger.web_trigger import WebTrigger
from servey.servey_aws.serverless.trigger_handler.trigger_handler_abc import (
    TriggerHandlerABC,
)


class WebTriggerHandler(TriggerHandlerABC):
    def handle_trigger(
        self,
        action: Action,
        trigger: TriggerABC,
        lambda_definition: ExternalItemType,
    ):
        if not isinstance(trigger, WebTrigger):
            return
        events = lambda_definition.get("events")
        if not events:
            events = lambda_definition["events"] = []
        events.append(
            dict(http=dict(path=action.name, method=trigger.method.value, cors=True))
        )
