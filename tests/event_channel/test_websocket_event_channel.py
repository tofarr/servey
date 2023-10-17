from unittest import TestCase
from unittest.mock import MagicMock, patch

from servey.action.action import action
from servey.errors import ServeyError
from servey.event_channel.background.background_action_channel import (
    background_action_channel,
)
from servey.event_channel.websocket.websocket_event_channel import (
    websocket_event_channel,
)


class TestWebsocketEventChannel(TestCase):
    def test_websocket_event_sender_no_factories(self):
        mock = MagicMock()
        mock.return_value = []
        with patch(
            "servey.event_channel.websocket.websocket_event_channel.get_impls", mock
        ):
            with self.assertRaises(ServeyError):
                websocket_event_channel("foobar", int)
