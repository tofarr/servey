from abc import ABC, abstractmethod
from typing import Callable, Tuple, List, TYPE_CHECKING

from servey.action.action_meta import ActionMeta
from servey.action.trigger.web_trigger import WebTrigger

if TYPE_CHECKING:
    from servey.servey_strawberry.schema_factory import SchemaFactory


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
        fn: Callable,
        action_meta: ActionMeta,
        trigger: WebTrigger,
        schema_factory: "SchemaFactory",
    ) -> Tuple[Callable, ActionMeta, bool]:
        """Filter the action given. The callable is a function"""


def create_handler_filters() -> Tuple[HandlerFilterABC]:
    from marshy.factory.impl_marshaller_factory import get_impls

    filters: List[HandlerFilterABC] = [f() for f in get_impls(HandlerFilterABC)]
    filters.sort(key=lambda f: f.priority, reverse=True)
    return tuple(filters)
