from marshy.types import ExternalItemType

from servey.action.action_meta import ActionMeta
from servey.action.trigger.trigger_abc import TriggerABC
from servey.action.trigger.web_trigger import WebTrigger
from servey.servey_aws.serverless.trigger_handler.trigger_handler_abc import (
    TriggerHandlerABC,
)


class WebTriggerHandler(TriggerHandlerABC):
    def handle_trigger(
        self,
        action_meta: ActionMeta,
        trigger: TriggerABC,
        lambda_definition: ExternalItemType,
    ):
        if not isinstance(trigger, WebTrigger):
            return
        events = lambda_definition.get("events")
        if not events:
            events = lambda_definition["events"] = []
        events.append(
            dict(
                http=dict(path=action_meta.name, method=trigger.method.value, cors=True)
            )
        )
