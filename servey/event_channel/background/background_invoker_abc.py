from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional

from servey.action.action import Action

T = TypeVar("T")


class BackgroundInvokerABC(Generic[T], ABC):
    @abstractmethod
    def invoke(self, event: T, delay: int = 0):
        """invoke a background action"""


class BackgroundInvokerFactoryABC(ABC):
    priority: int = 100

    @abstractmethod
    def create(self, action: Action, name: str) -> Optional[BackgroundInvokerABC]:
        """Create a background invoker for the channel and event_channel schema given if possible"""
