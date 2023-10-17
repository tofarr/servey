from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class EventChannelABC(Generic[T], ABC):
    """
    A channel represents something which can receive events - be it a background process, web hook, client web socket,
    or something else.
    """

    name: str

    @abstractmethod
    def publish(self, event: T):
        """Publish the event_channel given to this channel"""
