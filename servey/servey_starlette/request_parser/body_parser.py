import json
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple

from marshy.marshaller.marshaller_abc import MarshallerABC
from marshy.types import ExternalItemType
from schemey import Schema
from schemey.util import filter_none
from starlette.exceptions import HTTPException
from starlette.requests import Request

from servey.action.example import Example
from servey.servey_starlette.request_parser.request_parser_abc import RequestParserABC
from servey.action.util import with_isolated_references


@dataclass
class BodyParser(RequestParserABC):
    """
    Parser which pulls kwargs from a request body
    """

    schema: Schema
    marshaller: MarshallerABC

    async def parse(self, request: Request) -> Dict[str, Any]:
        body = await request.body()
        params: ExternalItemType = json.loads(body) if body else {}
        error = next(self.schema.iter_errors(params), None)
        if error:
            raise HTTPException(422, str(error))
        kwargs = self.marshaller.load(params)
        return kwargs

    def to_openapi_schema(
        self, path_method: ExternalItemType, components: ExternalItemType, examples: Optional[Tuple[Example, ...]]
    ):
        schema = with_isolated_references(
            self.schema.schema, self.schema.schema, components
        )
        content = {"schema": schema}
        path_method["requestBody"] = {
            "content": {"application/json": content},
            "required": True,
        }
        if examples:
            content['examples'] = {
                e.name: filter_none(dict(summary=e.description, value=e.result))
                for e in examples if e.include_in_schema
            }
        responses: ExternalItemType = path_method["responses"]
        responses["422"] = {"description": "Validation Error"}
