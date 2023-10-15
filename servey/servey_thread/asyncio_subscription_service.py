import asyncio
from asyncio import get_event_loop
from dataclasses import dataclass
from typing import Optional, List

from servey.servey_aws import is_lambda_env
from servey.servey_celery import has_celery_broker
from servey.subscription.delayed import Delayed
from servey.subscription.subscription import Subscription, T
from servey.subscription.subscription_service import (
    SubscriptionServiceABC,
    SubscriptionServiceFactoryABC,
)


@dataclass
class AsyncioSubscriptionService(SubscriptionServiceABC):
    """Subscription service backed by asyncio"""

    def publish(
        self,
        subscription: Subscription[T],
        event: T,
    ):
        loop = get_event_loop()
        for action in subscription.action_subscribers:
            # loop.call_soon_threadsafe(action.fn, event)
            asyncio.run_coroutine_threadsafe(action_fn(action.fn, event), loop)


class AsyncioSubscriptionServiceFactory(SubscriptionServiceFactoryABC):
    def create(
        self, subscriptions: List[Subscription]
    ) -> Optional[SubscriptionServiceABC]:
        if is_lambda_env() or has_celery_broker():
            # lambda environment, uses SQS instead, and if celery is
            # present we should use it
            return
        has_subscribers_with_actions = next(
            (True for s in subscriptions if s.action_subscribers), False
        )
        if has_subscribers_with_actions:
            return AsyncioSubscriptionService()


async def action_fn(action_fn, event):
    if isinstance(action_fn, Delayed):
        await asyncio.sleep(action_fn.delay_seconds)
    return action_fn(event)
