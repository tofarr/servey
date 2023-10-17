import asyncio
import os
from asyncio import sleep
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
        async def accumulator(value: int):
            nonlocal total
            total += value

        factory = AsyncioBackgroundInvokerFactory()
        invoker = factory.create(get_action(accumulator), "accumulator")
        invoker.invoke(3, 1)
        invoker.invoke(5)
        invoker.invoke(7)
        loop = asyncio.get_event_loop()

        loop.run_until_complete(sleep(1.1))
        self.assertEqual(15, total)
