from abc import abstractmethod, ABC
from inspect import Parameter
from typing import Optional, List

from servey.action import Action
from servey.integration.strawberry_integration.injector.injector_abc import InjectorABC


class InjectorFactoryABC(ABC):
    priority: int = 100

    @abstractmethod
    def create_injector(
        self, action: Action, parameters: List[Parameter]
    ) -> Optional[InjectorABC]:
        """Create a field if possible"""
