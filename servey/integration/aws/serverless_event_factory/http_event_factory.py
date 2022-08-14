from dataclasses import dataclass
from typing import Optional

from marshy.types import ExternalItemType

from servey.action_meta import ActionMeta
from servey.integration.aws.serverless_event_factory.serverless_event_factory_abc import (
    ServerlessEventFactoryABC,
)
from servey.trigger.web_trigger import WebTrigger


@dataclass
class HttpEventFactory(ServerlessEventFactoryABC):
    priority: int = 100
    path_pattern: str = "/actions/{action_name}"

    def create_event(self, action_meta: ActionMeta) -> Optional[ExternalItemType]:
        trigger = next(
            (t for t in action_meta.triggers if isinstance(t, WebTrigger)), None
        )
        if not trigger:
            return
        result = {
            "http": {
                "method": "post" if trigger.is_mutation else "get",
                "path": self.path_pattern.format(action_name=action_meta.name),
            }
        }
        return result
