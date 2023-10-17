from abc import abstractmethod, ABC
from typing import Iterator, TypeVar, Type

from marshy.factory.impl_marshaller_factory import get_impls

from servey.event_channel.event_channel_abc import EventChannelABC

T = TypeVar("T")


class EventChannelFinderABC(ABC):
    priority: int = 100

    @abstractmethod
    def find_event_channels(self) -> Iterator[EventChannelABC]:
        """Find all available channels"""


def find_event_channels() -> Iterator[EventChannelABC]:
    channel_finders = get_impls(EventChannelFinderABC)
    for channel_finder in channel_finders:
        finder = channel_finder()
        yield from finder.find_event_channels()


def find_event_channels_by_type(channel_type: Type[T]) -> Iterator[T]:
    for channel in find_event_channels():
        if isinstance(channel, channel_type):
            yield channel
