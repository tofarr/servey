from abc import abstractmethod, ABC
from typing import Iterator
from threading import Thread


class ThreadFactoryABC(ABC):
    """
    Factory for threads when running in threaded mode
    """

    @abstractmethod
    def create_threads(self, daemon: bool) -> Iterator[Thread]:
        """Create and yield execution threads"""
