from abc import abstractmethod, ABC
from typing import Any, Dict, Set


class InjectorABC(ABC):
    priority: int = 100

    @abstractmethod
    def inject(self, executor: Any, kwargs: Dict[str, Any], to_exclude: Set[str]):
        """Inject parameters"""
