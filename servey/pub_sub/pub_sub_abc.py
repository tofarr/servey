from abc import ABC
from typing import Optional, Iterable

from marshy.types import ExternalItemType


class PubSubABC(ABC):

    def publish(self, channel_id: str, event: ExternalItemType, subscriber_id: Optional[str]):
        pass

    def subscribe(self, channel_id: str, subscriber_id: Optional[str]):
        pass

    def is_subscribed(self, channel_id: str, subscriber_id: str) -> bool:
        pass

    def list_subscribers(self, channel_id: str) -> Iterable[str]:
        pass