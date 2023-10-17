import inspect
from dataclasses import dataclass
from typing import Union, Callable, Optional

from marshy.factory.impl_marshaller_factory import get_impls

from servey.action.action import Action, get_action
from servey.errors import ServeyError
from servey.event_channel.background.background_invoker_abc import (
    BackgroundInvokerFactoryABC,
)
from servey.event_channel.event_channel_abc import EventChannelABC, T


@dataclass(frozen=True)
class BackgroundActionChannel(EventChannelABC[T]):
    """
    Publisher which passes an event_channel to a background action for processing
    """

    action: Action
    delay: int = 0

    def publish(self, event: T):
        self.get_background_invoker().invoke(event, self.delay)

    def get_background_invoker(self):
        background_invoker = getattr(self, "_background_invoker", None)
        if background_invoker:
            return background_invoker
        sig = inspect.signature(self.action.fn)
        if len(sig.parameters) != 1:
            raise ServeyError(
                f"background_process_must_take_single_argument:{self.action.name}"
            )
        factories = [impl() for impl in get_impls(BackgroundInvokerFactoryABC)]
        factories.sort(key=lambda f: f.priority, reverse=True)
        for factory in factories:
            background_invoker = factory.create(self.action, self.name)
            if background_invoker:
                object.__setattr__(self, "_background_invoker", background_invoker)
                return background_invoker
        raise ServeyError(f"no_invoker_for_channel:{self.name}")


def background_action_channel(
    action: Union[Action, Callable], delay: int = 0, name: Optional[str] = None
):
    if not isinstance(action, Action):
        action = get_action(action)
    if not name:
        name = action.name
    return BackgroundActionChannel(name, action, delay)
