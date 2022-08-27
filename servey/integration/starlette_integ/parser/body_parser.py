from dataclasses import dataclass
from typing import Tuple, Optional, Dict, Any

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
class BodyParser(ParserABC):
    """
    Parser which pulls kwargs from a request body
    """

    action: Action

    async def parse(self, request: Request) -> Tuple[Executor, Dict[str, Any]]:
        executor = self.action.create_executor()
        params: ExternalItemType = await request.json()
        self.action.action_meta.params_schema.validate(params)
        kwargs = self.action.action_meta.params_marshaller.load(params)
        return executor, kwargs

    def to_openapi_schema(
        self, path_method: ExternalItemType, components: ExternalItemType
    ):
        schema = self.action.action_meta.result_schema
        schema = with_isolated_references(schema.schema, schema.schema, components)
        path_method["requestBody"] = {
            "content": {"application/json": {"schema": schema}},
            "required": True,
        }


class BodyParserFactory(ParserFactoryABC):
    priority: int = 50

    def create(
        self,
        action: Action,
        trigger: WebTrigger,
        parser_factories: Tuple[ParserFactoryABC],
    ) -> Optional[ParserABC]:
        if trigger.method in BODY_METHODS:
            return BodyParser(action)
