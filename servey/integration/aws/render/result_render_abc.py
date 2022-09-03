from abc import abstractmethod, ABC
from typing import Any

from starlette.responses import JSONResponse

from servey.executor import Executor


class ResultRenderABC(ABC):
    @abstractmethod
    def render(self, executor: Executor, result: Any) -> JSONResponse:
        """Render the result given"""
