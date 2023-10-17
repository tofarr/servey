import os
from unittest import TestCase

from servey.finder.module_event_channel_finder import ModuleEventChannelFinder


class TestModuleSubscriptionFinder(TestCase):
    def test_default_constructor(self):
        finder = ModuleEventChannelFinder()
        self.assertEqual(ModuleEventChannelFinder("servey_main.event_channels"), finder)
        os.environ["SERVEY_MAIN"] = "foobar"
        finder = ModuleEventChannelFinder()
        self.assertEqual(ModuleEventChannelFinder("foobar.event_channels"), finder)
        os.environ.pop("SERVEY_MAIN")

    def test_find_event_channels(self):
        from tests.finder.event_channels.test_event_channel import my_channel

        finder = ModuleEventChannelFinder("tests.finder.event_channels")
        channels = list(finder.find_event_channels())
        expected = [my_channel]
        self.assertEqual(expected, channels)

    def test_find_event_channels_not_found(self):
        finder = ModuleEventChannelFinder("this.module.does.not.exist")
        self.assertEqual([], list(finder.find_event_channels()))
