from __future__ import annotations
from abc import abstractmethod, ABC
from typing import Any, Dict

from marshy.types import ExternalItemType
from starlette.requests import Request


class RequestParserABC(ABC):
    @abstractmethod
    async def parse(self, request: Request) -> Dict[str, Any]:
        """Parse a request"""

    @abstractmethod
    def to_openapi_schema(
        self, path_method: ExternalItemType, components: ExternalItemType
    ):
        """Add an openapi description of this parser to the openapi path/method given"""
