import asyncio
import os
from unittest import TestCase
from unittest.mock import patch

from servey.action.action import action, get_action
from servey.servey_thread.asyncio_background_invoker import (
    AsyncioBackgroundInvokerFactory,
)


class TestAsyncioBackgroundInvoker(TestCase):
    def test_invoker(self):
        total = 0

        @action
        def accumulator(value: int):
            nonlocal total
            total += value

        factory = AsyncioBackgroundInvokerFactory()
        invoker = factory.create(get_action(accumulator))
        invoker.invoke(3)
        invoker.invoke(5)
        invoker.invoke(7)
        loop = asyncio.get_event_loop()

        async def dummy():
            pass

        loop.run_until_complete(dummy())
        self.assertEqual(15, total)
