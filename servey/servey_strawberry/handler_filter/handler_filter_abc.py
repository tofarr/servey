from abc import ABC, abstractmethod
from typing import Tuple

from servey.action.action import Action


class HandlerFilterABC(ABC):
    """
    Sometimes the default behaviour from strawberry is not quite what we want, so this allows us to customize
    how a strawberry object is converted to / from regular python
    Examples include adding authorization
    """

    priority: int = 100

    # noinspection PyUnresolvedReferences
    @abstractmethod
    def filter(
        self,
        action: Action,
        schema_factory: "servey.servey_strawberry.schema_factory.SchemaFactory",
    ) -> Tuple[Action, bool]:
        """Filter the action_ given. The callable is a function"""
