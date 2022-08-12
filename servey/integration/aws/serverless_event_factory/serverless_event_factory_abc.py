from abc import ABC, abstractmethod
from typing import Optional

from marshy.types import ExternalItemType

from servey.action_meta import ActionMeta


class ServerlessEventFactoryABC(ABC):
    priority: int = 100

    @abstractmethod
    def create_event(self, action_meta: ActionMeta) -> Optional[ExternalItemType]:
        """ Create an event based on the trigger given"""
