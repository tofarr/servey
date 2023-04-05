from typing import Optional

from marshy.types import ExternalItemType

from servey.action.action import Action
from servey.errors import ServeyError
from servey.servey_aws.event_handler.event_handler_abc import (
    get_event_handlers,
    EventHandlerABC,
)
from servey.servey_aws.router.router_abc import RouterABC


class AppsyncRouter(RouterABC):
    priority: int = 110

    def create_handler(self, event: ExternalItemType, context) -> EventHandlerABC:
        info = event.get("info", None)  # Diff appsync events
        if info is None:
            return
        field_name = info["fieldName"]
        action = self.find_action_for_field_name(field_name)
        if action is None:
            raise ServeyError(f"unknown_field_name:{field_name}")
        handlers = get_event_handlers(action)
        for handler in handlers:
            if handler.is_usable(event, context):
                return handler

    def find_action_for_field_name(self, field_name: str) -> Optional[Action]:
        for action, trigger in self.web_trigger_actions:
            action_field_name = action.name[0] + action.name.title()[1:].replace(
                "_", ""
            )
            if action_field_name == field_name:
                return action
