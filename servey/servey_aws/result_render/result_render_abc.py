from abc import ABC, abstractmethod
from typing import Any

from marshy import ExternalType


class ResultRenderABC(ABC):
    @abstractmethod
    def render_result(self, result: Any) -> ExternalType:
        """Render a result"""
