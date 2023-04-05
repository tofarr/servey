from abc import ABC, abstractmethod
from typing import Tuple

from marshy.factory.impl_marshaller_factory import get_impls
from marshy.types import ExternalItemType

from servey.action.action import Action
from servey.finder.action_finder_abc import find_actions_with_trigger_type
from servey.servey_aws.event_handler.event_handler_abc import EventHandlerABC
from servey.trigger.web_trigger import WebTrigger


class RouterABC(ABC):
    """A router will attempt to create an event handler given a specific lambda event"""

    priority: int = 100

    @abstractmethod
    def create_handler(self, event: ExternalItemType, context) -> EventHandlerABC:
        """Create a handler for the event given"""

    @property
    def web_trigger_actions(self) -> Tuple[Tuple[Action, WebTrigger], ...]:
        web_trigger_actions = getattr(self, "_web_trigger_actions", None)
        if web_trigger_actions is None:
            web_trigger_actions = list(find_actions_with_trigger_type(WebTrigger))
            web_trigger_actions.sort(
                key=lambda n: len(n[1].path or f"/actions/{n[0].name}"), reverse=True
            )
            web_trigger_actions = tuple(web_trigger_actions)
            setattr(self, "_web_trigger_actions", web_trigger_actions)
        return web_trigger_actions


def find_routers() -> Tuple[RouterABC]:
    routers = [router() for router in get_impls(RouterABC)]
    routers.sort(key=lambda r: r.priority, reverse=True)
    return tuple(routers)
