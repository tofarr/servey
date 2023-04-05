from marshy.types import ExternalItemType

from servey.finder.action_finder_abc import find_actions
from servey.servey_aws.event_handler.event_handler_abc import (
    get_event_handlers,
    EventHandlerABC,
)
from servey.servey_aws.router.router_abc import RouterABC


class Router(RouterABC):
    def create_handler(self, event: ExternalItemType, context) -> EventHandlerABC:
        action_name = event.get("action_name", None)
        if action_name is None:
            return
        action = next(a for a in find_actions() if a.name == action_name)
        handlers = get_event_handlers(action)
        for handler in handlers:
            if handler.is_usable(event, context):
                return handler
