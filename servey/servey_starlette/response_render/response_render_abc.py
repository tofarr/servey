from abc import abstractmethod, ABC
from typing import Any, Dict, Optional, Tuple

from marshy.types import ExternalItemType
from requests import Response

from servey.action.example import Example


class ResponseRenderABC(ABC):
    @abstractmethod
    def render(self, kwargs: Dict[str, Any], result: Any) -> Response:
        """Render a response"""

    @abstractmethod
    def to_openapi_schema(
        self, responses: ExternalItemType, components: ExternalItemType, examples: Optional[Tuple[Example, ...]]
    ):
        """Add an openapi description of this render to the openapi path/method/responses given"""
