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
class QueryStringParser(RequestParserABC):
    """
    Parser which pulls kwargs from a request query string
    """

    schema: Schema
    marshaller: MarshallerABC

    async def parse(self, request: Request) -> Dict[str, Any]:
        params = dict(request.query_params)
        error = next(self.schema.iter_errors(params), None)
        if error:
            raise HTTPException(422, str(error))
        kwargs = self.marshaller.load(params)
        return kwargs

    def to_openapi_schema(
        self, path_method: ExternalItemType, components: ExternalItemType, examples: Optional[Tuple[Example, ...]]
    ):
        schema = self.schema
        properties = schema.schema["properties"]
        required = set(schema.schema.get("required") or [])
        path_method["parameters"] = [
            filter_none({
                "required": k in required,
                "schema": with_isolated_references(schema.schema, v, components),
                "name": k,
                "in": "query",
                "examples": {
                    e.name: filter_none(dict(summary=e.description, value=e.result))
                    for e in examples if e.include_in_schema
                } if examples else None
            })
            for k, v in properties.items()
        ]
        responses: ExternalItemType = path_method["responses"]
        responses["422"] = {"description": "Validation Error"}
