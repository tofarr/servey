from dataclasses import dataclass
from typing import Optional, Callable, Tuple, Union

from servey.action.batch_invoker import BatchInvoker
from servey.action.example import Example
from servey.cache_control.cache_control_abc import CacheControlABC
from servey.security.access_control.access_control_abc import (
    AccessControlABC,
)
from servey.security.access_control.allow_all import ALLOW_ALL
from servey.trigger.trigger_abc import TriggerABC


@dataclass(frozen=True)
class Action:
    """
    Actions provide additional meta about a function and how it should be invoked from an external context such as REST,
    GraphQL, Tests, Mocks, or a scheduler. The intent is that everything required to document and invoke the function
    should be present here
    """

    fn: Callable
    name: str
    description: Optional[str] = None
    access_control: AccessControlABC = ALLOW_ALL
    triggers: Tuple[TriggerABC, ...] = tuple()
    timeout: int = 15
    examples: Optional[Tuple[Example, ...]] = None
    cache_control: Optional[CacheControlABC] = None
    batch_invoker: Optional[BatchInvoker] = None


def action(
    fn: Optional[Callable] = None,
    access_control: AccessControlABC = Action.access_control,
    triggers: Union[TriggerABC, Tuple[TriggerABC, ...]] = Action.triggers,
    timeout: int = Action.timeout,
    examples: Optional[Tuple[Example, ...]] = None,
    cache_control: Optional[CacheControlABC] = None,
    batch_invoker: Optional[BatchInvoker] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
):
    """
    Decorator for actions, which may be a function or a class with a designated method_name
    to act as the action_. This decorator doesn't really do anything special aside from
    adding metadata to the object which may be interpreted when the action_ is mounted.

    When mounting, operations like security checks and validations are performed, as well as
    parameter injection for class based actions.
    """

    if isinstance(triggers, TriggerABC):
        triggers = (triggers,)

    def wrapper_(fn_: Callable):
        fn_.__servey_action__ = get_action_for_fn(fn_)
        return fn_

    def get_action_for_fn(fn_: Callable):
        return Action(
            fn=fn_,
            name=name or fn_.__name__,
            description=description or (fn_.__doc__.strip() if fn_.__doc__ else None),
            access_control=access_control,
            triggers=triggers,
            timeout=timeout,
            examples=examples,
            cache_control=cache_control,
            batch_invoker=batch_invoker,
        )

    return wrapper_ if fn is None else wrapper_(fn)


def get_action(fn: Callable) -> Optional[Action]:
    return getattr(fn, "__servey_action__", None)
