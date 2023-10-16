from dataclasses import dataclass

from servey.event_channel.websocket.websocket_channel import websocket_channel


@dataclass
class MyEvent:
    msg: str


my_channel = websocket_channel("my_channel", MyEvent)
