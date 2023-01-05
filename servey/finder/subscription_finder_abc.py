from abc import abstractmethod, ABC
from typing import Iterator, TypeVar

from marshy.factory.impl_marshaller_factory import get_impls

from servey.subscription.subscription import Subscription

T = TypeVar("T")


class SubscriptionFinderABC(ABC):
    priority: int = 100

    @abstractmethod
    def find_subscriptions(self) -> Iterator[Subscription]:
        """Find all available subscriptions"""


def find_subscriptions() -> Iterator[Subscription]:
    subscription_finders = get_impls(SubscriptionFinderABC)
    for subscription_finder in subscription_finders:
        finder = subscription_finder()
        yield from finder.find_subscriptions()
