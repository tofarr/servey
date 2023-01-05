from abc import abstractmethod, ABC
from typing import List, Optional

from marshy.factory.impl_marshaller_factory import get_impls
from marshy.types import ExternalItemType, ExternalType

from servey.action.action import Action


class EventHandlerABC(ABC):
    priority: int = 100

    @abstractmethod
    def is_usable(self, event: ExternalItemType, context) -> bool:
        """Determine if this handler is usable for the event and context given"""

    @abstractmethod
    def handle(self, event: ExternalItemType, context) -> ExternalType:
        """Handle the event given and return a result"""


class EventHandlerFactoryABC(ABC):
    @abstractmethod
    def create(self, action: Action) -> Optional[EventHandlerABC]:
        """Create a handler for the action given"""


def get_event_handlers(action: Action) -> List[EventHandlerABC]:
    handlers = [
        factory().create(action) for factory in get_impls(EventHandlerFactoryABC)
    ]
    handlers = [h for h in handlers if h]
    handlers.sort(key=lambda h: h.priority, reverse=True)
    return handlers
