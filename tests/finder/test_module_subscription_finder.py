import os
from unittest import TestCase

from servey.finder.module_subscription_finder import ModuleSubscriptionFinder


class TestModuleSubscriptionFinder(TestCase):
    def test_default_constructor(self):
        finder = ModuleSubscriptionFinder()
        self.assertEqual(ModuleSubscriptionFinder("servey_main.subscriptions"), finder)
        os.environ["SERVEY_MAIN"] = "foobar"
        finder = ModuleSubscriptionFinder()
        self.assertEqual(ModuleSubscriptionFinder("foobar.subscriptions"), finder)
        os.environ.pop("SERVEY_MAIN")

    def test_find_subscriptions(self):
        from tests.finder.subscriptions.test_subscriptions import my_subscription

        finder = ModuleSubscriptionFinder("tests.finder.subscriptions")
        subscriptions = list(finder.find_subscriptions())
        expected = [my_subscription]
        self.assertEqual(expected, subscriptions)

    def test_find_subscriptions_not_found(self):
        finder = ModuleSubscriptionFinder("this.module.does.not.exist")
        self.assertEqual([], list(finder.find_subscriptions()))
