from marshy.types import ExternalItemType

from servey.errors import ServeyError
from servey.servey_aws.event_handler.event_handler_abc import (
    get_event_handlers,
    EventHandlerABC,
)
from servey.servey_aws.router.router_abc import RouterABC


class APIGatewayRouter(RouterABC):
    priority: int = 120

    def create_handler(self, event: ExternalItemType, context) -> EventHandlerABC:
        path = event.get("path", None)
        if path is None:
            return
        action = self.find_action_for_path(path)
        if action is None:
            raise ServeyError(f"unknown_path:{path}")
        handlers = get_event_handlers(action)
        for handler in handlers:
            if handler.is_usable(event, context):
                return handler
