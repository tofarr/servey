from abc import abstractmethod
from typing import Iterator

from starlette.routing import Route


class RouteFactoryABC:
    priority: int = 100

    @abstractmethod
    def create_routes(self) -> Iterator[Route]:
        """Create routes"""
