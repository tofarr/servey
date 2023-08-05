from abc import ABC, abstractmethod
from typing import Optional

from starlette.middleware import Middleware


class MiddlewareFactoryABC(ABC):
    priority: int = 100

    @abstractmethod
    def create(self) -> Optional[Middleware]:
        """Optionally create middleware for the application - used for things like cors"""
