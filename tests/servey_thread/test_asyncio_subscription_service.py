import asyncio
import os
from unittest import TestCase
from unittest.mock import patch

from servey.action.action import action, get_action
from servey.servey_thread.asyncio_subscription_service import (
    AsyncioSubscriptionServiceFactory,
)
from servey.subscription.subscription import subscription


class TestAsyncioSubscriptionService(TestCase):
    def test_subscriptions(self):
        total = 0

        @action
        def accumulator(value: int):
            nonlocal total
            total += value

        subscription_ = subscription(
            event_type=int,
            name="accumulators",
            action_subscribers=(get_action(accumulator),),
        )
        factory = AsyncioSubscriptionServiceFactory()
        service = factory.create([subscription_])
        service.publish(subscription_, 3)
        service.publish(subscription_, 5)
        service.publish(subscription_, 7)
        loop = asyncio.get_event_loop()

        async def dummy():
            pass

        loop.run_until_complete(dummy())
        self.assertEqual(15, total)

    def test_disabled_with_lambda(self):
        with patch.dict(os.environ, {"AWS_REGION": "bezos-moon-base"}):
            factory = AsyncioSubscriptionServiceFactory()
            subscription_ = subscription(event_type=int, name="accumulators")
            self.assertIsNone(factory.create([subscription_]))
