from marshy.types import ExternalItemType

from servey.action.action import Action
from servey.trigger.trigger_abc import TriggerABC
from servey.trigger.web_trigger import WebTrigger
from servey.servey_aws.serverless.trigger_handler.trigger_handler_abc import (
    TriggerHandlerABC,
)


class WebTriggerHandler(TriggerHandlerABC):
    """
    Handler which outputs serverless definitions for api gateway triggers.
    """

    path_pattern: str = "/actions/{action_name}"

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
        path = trigger.path or self.path_pattern.format(
            action_name=action.name.replace("_", "-")
        )
        events.append(
            dict(http=dict(path=path, method=trigger.method.value, cors=True))
            # TODO: Add openapi documentation
        )
