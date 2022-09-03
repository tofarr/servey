from abc import ABC, abstractmethod
from typing import Optional

from marshy import ExternalType
from marshy.types import ExternalItemType

from servey.action import Action


class LambdaHandlerABC(ABC):
    @abstractmethod
    def __call__(self, event: ExternalItemType, context) -> ExternalType:
        """Invoke this lambda"""

    @abstractmethod
    def get_action(self) -> Action:
        """Get the action for this handler"""


class LambdaHandlerFactory(ABC):
    @abstractmethod
    def create_lambda_handler(self, action: Action) -> Optional[LambdaHandlerABC]:
        """Create a lambda handler for the action given"""
