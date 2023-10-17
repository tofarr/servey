from unittest import TestCase
from unittest.mock import MagicMock, patch

from servey.action.action import action
from servey.errors import ServeyError
from servey.event_channel.background.background_action_channel import (
    background_action_channel,
)


class TestBackgroundActionChannel(TestCase):
    def test_get_background_invoker(self):
        @action
        def dummy(value: int):
            """A dummy"""

        channel = background_action_channel(dummy)
        self.assertIs(
            channel.get_background_invoker(), channel.get_background_invoker()
        )

    def test_get_background_invoker_invalid(self):
        @action
        def dummy(foo: int, bar: int):
            """A dummy"""

        channel = background_action_channel(dummy)
        with self.assertRaises(ServeyError):
            channel.get_background_invoker()

    def test_get_background_invoker_no_factories(self):
        @action
        def dummy(foo: int):
            """A dummy"""

        mock = MagicMock()
        mock.return_value = []
        with patch(
            "servey.event_channel.background.background_action_channel.get_impls", mock
        ):
            channel = background_action_channel(dummy)
            with self.assertRaises(ServeyError):
                channel.get_background_invoker()
