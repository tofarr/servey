from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional

from servey.security.authorization import Authorization

T = TypeVar("T")


class EventFilterABC(ABC, Generic[T]):
    @abstractmethod
    def should_publish(self, event: T, authorization: Optional[Authorization]) -> bool:
        """Filter the event given depending on the authorization of the subscriber"""
