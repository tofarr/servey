from marshy.types import ExternalItemType

from servey.action.action import Action
from servey.cors import get_allowed_origins
from servey.errors import ServeyError
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
        event = {"http": {"path": path, "method": trigger.method.value}}
        allowed_origins = get_allowed_origins()
        if allowed_origins:
            if len(allowed_origins) > 1:
                raise ServeyError("multi_origin_unsupported")
            event["http"]["cors"] = {
                "origin": allowed_origins[0],
                "allowCredentials": True,
            }
        events.append(event)
