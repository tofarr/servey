from typing import List, Optional

from servey.subscription.subscription import Subscription, T
from servey.subscription.subscription_service import (
    SubscriptionServiceABC,
    SubscriptionServiceFactoryABC,
)


class CelerySubscriptionService(SubscriptionServiceABC):
    """
    Service designed to work with celery to cluster subscriptions.
    """

    def publish(self, subscription: Subscription[T], event: T):
        from servey.servey_celery import celery_app

        for action in subscription.action_subscribers:
            task = getattr(celery_app, action.name)
            task.delay(*[event])


class CelerySubscriptionServiceFactory(SubscriptionServiceFactoryABC):
    """
    Factory which sets up a celery subscription service only if a celery
    broker was specified
    """

    def create(
        self, subscriptions: List[Subscription]
    ) -> Optional[SubscriptionServiceABC]:
        from servey.servey_celery import has_celery_broker

        if has_celery_broker():
            return CelerySubscriptionService()
