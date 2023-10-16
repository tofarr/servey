from servey.action.action import get_action
from servey.event_channel.background.background_action_channel import (
    background_action_channel,
)

from servey.event_channel.websocket.websocket_channel import websocket_channel
from servey_main.actions import print_consumer

messenger = websocket_channel("messenger", str)

printer = background_action_channel(get_action(print_consumer))
