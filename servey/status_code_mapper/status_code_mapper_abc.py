from abc import abstractmethod, ABC
from typing import TypeVar, Generic

T = TypeVar("T")


class StatusCodeMapperABC(ABC, Generic[T]):
    @property
    @abstractmethod
    def status_code(self) -> int:
        """Get the status code for this mapper"""

    @abstractmethod
    def match(self, result: T) -> bool:
        """Determine if this mapper matches the result given"""

    @abstractmethod
    def description(self) -> str:
        """Get the description for this mapper"""
