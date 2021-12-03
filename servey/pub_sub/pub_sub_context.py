from marshy import ExternalType


class PubSubContextABC(ABC):

    def publish(self, channel_id: str, event: ExternalItemType):
        pass

    def subscribe(self, channel_id: str, callback: Callable[ExternalItemType]):
        pass

    def on_subscribe(self):