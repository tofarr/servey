from abc import abstractmethod, ABC
from typing import Iterator, Type, Tuple, TypeVar

from marshy.factory.impl_marshaller_factory import get_impls

from servey.action.action import Action

T = TypeVar("T")


class ActionFinderABC(ABC):
    priority: int = 100

    @abstractmethod
    def find_actions(self) -> Iterator[Action]:
        """Find all available actions"""


def find_actions() -> Iterator[Action]:
    action_finders = get_impls(ActionFinderABC)
    for action_finder in action_finders:
        finder = action_finder()
        yield from finder.find_actions()


def find_actions_with_trigger_type(
    trigger_type: Type[T],
) -> Iterator[Tuple[Action, T]]:
    for action in find_actions():
        for trigger in action.triggers:
            if isinstance(trigger, trigger_type):
                yield action, trigger
