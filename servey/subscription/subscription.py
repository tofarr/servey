from dataclasses import dataclass
from typing import Generic, TypeVar, Optional, Type, Tuple

from marshy import get_default_context
from marshy.marshaller.marshaller_abc import MarshallerABC
from schemey import Schema, schema_from_type

from servey.action.action import Action
from servey.security.access_control.access_control_abc import AccessControlABC
from servey.security.access_control.allow_all import ALLOW_ALL
from servey.subscription.event_filter_abc import EventFilterABC

T = TypeVar("T")


@dataclass(frozen=True)
class Subscription(Generic[T]):
    name: str
    event_marshaller: MarshallerABC[T]
    event_schema: Schema
    access_control: AccessControlABC = ALLOW_ALL
    event_filter: Optional[EventFilterABC] = None
    action_subscribers: Tuple[Action, ...] = tuple()

    def publish(self, event: T):
        """
        Publish an event to subscribers
        """
        from servey.subscription.subscription_service import get_subscription_services

        for subscription_service in get_subscription_services():
            subscription_service.publish(self, event)


def subscription(
    event_type: Type[T],
    name: Optional[str] = None,
    access_control: AccessControlABC = ALLOW_ALL,
    event_filter: Optional[EventFilterABC] = None,
    action_subscribers: Tuple[Action] = tuple(),
) -> Subscription[T]:
    subscription_ = Subscription(
        event_marshaller=get_default_context().get_marshaller(event_type),
        event_schema=schema_from_type(event_type),
        name=name or event_type.__name__,
        access_control=access_control,
        event_filter=event_filter,
        action_subscribers=action_subscribers,
    )
    return subscription_
