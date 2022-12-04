from __future__ import annotations
from abc import abstractmethod, ABC
from typing import Any, Dict, Optional, Tuple

from marshy.types import ExternalItemType
from starlette.requests import Request

from servey.action.example import Example


class RequestParserABC(ABC):
    @abstractmethod
    async def parse(self, request: Request) -> Dict[str, Any]:
        """Parse a request"""

    @abstractmethod
    def to_openapi_schema(
        self, path_method: ExternalItemType, components: ExternalItemType, examples: Optional[Tuple[Example, ...]]
    ):
        """Add an openapi description of this parser to the openapi path/method given"""
