import asyncio
from asyncio import get_event_loop
from dataclasses import dataclass
from typing import Optional, Callable, Awaitable

from servey.action.action import Action
from servey.event_channel.background.background_invoker_abc import (
    BackgroundInvokerABC,
    BackgroundInvokerFactoryABC,
    T,
)


@dataclass
class AsyncioBackgroundInvoker(BackgroundInvokerABC):
    action: Action

    def invoke(self, event: T, delay: int = 0):
        loop = get_event_loop()
        asyncio.run_coroutine_threadsafe(action_fn(self.action.fn, event, delay), loop)


class AsyncioBackgroundInvokerFactory(BackgroundInvokerFactoryABC):
    priority: int = 50  # Low priority

    def create(self, action: Action, name: str) -> Optional[BackgroundInvokerABC]:
        return AsyncioBackgroundInvoker(action)


async def action_fn(fn: Callable, event: T, delay: int):
    if delay:
        await asyncio.sleep(delay)
    result = fn(event)
    if isinstance(result, Awaitable):
        result = await result
    return result
