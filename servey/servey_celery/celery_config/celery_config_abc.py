from abc import abstractmethod, ABC
from typing import Dict

from celery import Celery


class CeleryConfigABC(ABC):
    @abstractmethod
    def configure(self, app: Celery, global_ns: Dict):
        """
        Configure celery
        """
