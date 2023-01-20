from marshy.types import ExternalItemType

from servey.action.action import Action
from servey.servey_aws.serverless.trigger_handler.trigger_handler_abc import (
    TriggerHandlerABC,
)
from servey.servey_web_page.web_page_trigger import WebPageTrigger
from servey.trigger.trigger_abc import TriggerABC


class WebPageTriggerHandler(TriggerHandlerABC):
    def handle_trigger(
        self, action: Action, trigger: TriggerABC, lambda_definition: ExternalItemType
    ):
        if not isinstance(trigger, WebPageTrigger):
            return
        events = lambda_definition.get("events")
        if not events:
            events = lambda_definition["events"] = []
        path = trigger.path or f"/{action.name.replace('_', '-')}"
        events.append(
            dict(http=dict(path=path, method=trigger.method.value, cors=True))
        )
