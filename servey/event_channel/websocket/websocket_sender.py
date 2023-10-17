from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional

from schemey import Schema

from servey.event_channel.websocket.event_filter_abc import EventFilterABC
from servey.security.access_control.access_control_abc import AccessControlABC
from servey.security.access_control.allow_all import ALLOW_ALL

T = TypeVar("T")


class WebsocketSenderABC(Generic[T], ABC):
    """
    A Websocket sender is used to send events over a websocket to connected clients.
    """

    @abstractmethod
    def send(self, channel_name: str, event: T):
        """send an event_channel"""


class WebsocketSenderFactoryABC(ABC):
    priority: int = 100

    @abstractmethod
    def create(
        self,
        channel_name: str,
        event_schema: Schema,
        access_control: AccessControlABC = ALLOW_ALL,
        event_filter: Optional[EventFilterABC] = None,
    ) -> Optional[WebsocketSenderABC]:
        """Create a background invoker for the channel and event_channel schema given if possible"""
