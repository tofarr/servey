from abc import abstractmethod, ABC
from typing import Any, Dict

from marshy.types import ExternalItemType
from requests import Response


class ResponseRenderABC(ABC):
    @abstractmethod
    def render(self, kwargs: Dict[str, Any], result: Any) -> Response:
        """Render a response"""

    @abstractmethod
    def to_openapi_schema(
        self, responses: ExternalItemType, components: ExternalItemType
    ):
        """Add an openapi description of this render to the openapi path/method/responses given"""
