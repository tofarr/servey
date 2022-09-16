from abc import ABC, abstractmethod
from inspect import Signature
from typing import Callable, Tuple, Dict, Any, List

from servey.action import Action
from servey.executor import Executor
from servey.trigger.web_trigger import WebTrigger

ExecutorFn = Callable[[Executor, Dict[str, Any]], Any]
# String to prevent circular import
SchemaFactory = "servey.servey_strawberry.schema_factory.SchemaFactory"


class HandlerFilterABC(ABC):
    """
    Sometimes the default behaviour from strawberry is not quite what we want, so this allows us to customize
    how a strawberry object is converted to / from regular python
    Examples include adding authorization
    """

    priority: int = 100

    @abstractmethod
    def filter(
        self,
        action: Action,
        trigger: WebTrigger,
        fn: ExecutorFn,
        sig: Signature,
        schema_factory: SchemaFactory,
    ) -> Tuple[ExecutorFn, Signature, bool]:
        """Filter the action given. The callable is a function"""


def create_handler_filters() -> Tuple[HandlerFilterABC]:
    from marshy.factory.impl_marshaller_factory import get_impls

    filters: List[HandlerFilterABC] = [f() for f in get_impls(HandlerFilterABC)]
    filters.sort(key=lambda f: f.priority, reverse=True)
    return tuple(filters)
