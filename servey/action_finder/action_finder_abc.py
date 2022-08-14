from abc import abstractmethod, ABC
from typing import Iterator

from servey.action import Action


class ActionFinderABC(ABC):
    priority: int = 100

    @abstractmethod
    def find_actions(self) -> Iterator[Action]:
        """Create a new action context"""
