from dataclasses import dataclass

from servey.event_channel.websocket.websocket_event_channel import (
    websocket_event_channel,
)


@dataclass
class MyEvent:
    msg: str


my_channel = websocket_event_channel("my_channel", MyEvent)
