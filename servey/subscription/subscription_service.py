from abc import ABC, abstractmethod
from typing import Optional, Tuple, List

from marshy.factory.impl_marshaller_factory import get_impls

from servey.finder.subscription_finder_abc import find_subscriptions
from servey.subscription.subscription import Subscription, T


class SubscriptionServiceABC(ABC):
    """
    Service for sending messages to subscribed clients (Possibly by websocket)
    """

    @abstractmethod
    def publish(self, subscription: Subscription[T], event: T):
        """
        Send the event given to listeners on the subscription given.
        """


class SubscriptionServiceFactoryABC(ABC):
    priority: int = 100

    @abstractmethod
    def create(
        self, subscriptions: List[Subscription]
    ) -> Optional[SubscriptionServiceABC]:
        """
        Create a subscription service if the current environment supports it.
        """


_SUBSCRIPTION_SERVICES = None


def get_subscription_services() -> Tuple[SubscriptionServiceABC, ...]:
    global _SUBSCRIPTION_SERVICES
    if _SUBSCRIPTION_SERVICES is None:
        subscriptions = list(find_subscriptions())
        _SUBSCRIPTION_SERVICES = tuple(
            s
            for s in (
                f().create(subscriptions)
                for f in get_impls(SubscriptionServiceFactoryABC)
            )
            if s
        )
    return _SUBSCRIPTION_SERVICES
