from abc import ABC, abstractmethod

from marshy import ExternalType
from marshy.types import ExternalItemType

from servey.action import Action


class HandlerABC(ABC):
    @abstractmethod
    def invoke(self, event: ExternalItemType, context) -> ExternalType:
        """Invoke this lambda"""

    @abstractmethod
    def get_action(self) -> Action:
        """Get the action for this handler"""
