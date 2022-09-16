from dataclasses import dataclass
from typing import Dict, Any, Callable

from marshy.types import ExternalItemType
from starlette.requests import Request

from servey.servey_starlette.request_parser.request_parser_abc import RequestParserABC


@dataclass
class SelfParser(RequestParserABC):
    parser: RequestParserABC
    constructor: Callable
    self_name: str = "self"

    async def parse(self, request: Request) -> Dict[str, Any]:
        kwargs = await self.parser.parse(request)
        self_ = self.constructor()
        kwargs[self.self_name] = self_
        return kwargs

    def to_openapi_schema(
        self, path_method: ExternalItemType, components: ExternalItemType
    ):
        # Simply delegate - self should not be visible externally!
        return self.parser.to_openapi_schema(path_method, components)
