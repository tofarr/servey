from dataclasses import dataclass
from typing import Tuple, Dict, Any, Optional

from marshy.types import ExternalItemType
from starlette.requests import Request

from servey.action import Action
from servey.executor import Executor
from servey.integration.starlette_integ.parser.parser_abc import (
    ParserABC,
    ParserFactoryABC,
)
from servey.integration.starlette_integ.util import with_isolated_references
from servey.trigger.web_trigger import BODY_METHODS, WebTrigger


@dataclass
class QueryStringParser(ParserABC):
    """
    Parser which pulls kwargs from a request query string
    """

    action: Action

    async def parse(self, request: Request) -> Tuple[Executor, Dict[str, Any]]:
        executor = self.action.create_executor()
        params = request.query_params
        self.action.action_meta.params_schema.validate(params)
        kwargs = self.action.action_meta.params_marshaller.load(params)
        return executor, kwargs

    def to_openapi_schema(
        self, path_method: ExternalItemType, components: ExternalItemType
    ):
        schema = self.action.action_meta.result_schema
        properties = schema.schema["properties"]
        required = set(schema.schema.get("required") or [])
        path_method["parameters"] = [
            {
                "required": k in required,
                "schema": with_isolated_references(schema.schema, v, components),
                "name": k,
                "in": "query",
            }
            for k, v in properties.items()
        ]


class QueryStringParserFactory(ParserFactoryABC):
    priority: int = 50

    def create(
        self,
        action: Action,
        trigger: WebTrigger,
        parser_factories: Tuple[ParserFactoryABC],
    ) -> Optional[ParserABC]:
        if trigger.method not in BODY_METHODS:
            return QueryStringParser(action)
