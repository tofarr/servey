from marshy.types import ExternalItemType

from servey.servey_aws.event_handler.event_handler_abc import get_event_handlers, EventHandlerABC
from servey.servey_aws.router.router_abc import RouterABC


class AppsyncRouter(RouterABC):
    priority: int = 110

    def create_handler(self, event: ExternalItemType, context) -> EventHandlerABC:
        path = event.get('path', None)  # Diff appsync events
        if path is None:
            return
        action = self.find_action_for_path(path)
        handlers = get_event_handlers(action)
        for handler in handlers:
            if handler.is_usable(event, context):
                return handler
