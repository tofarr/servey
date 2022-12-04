from dataclasses import dataclass
from typing import Any, Optional, Dict, Tuple

from marshy.marshaller.marshaller_abc import MarshallerABC
from marshy.types import ExternalItemType
from schemey import Schema
from schemey.util import filter_none
from starlette.responses import JSONResponse, Response

from servey.action.example import Example
from servey.action.util import with_isolated_references
from servey.servey_starlette.response_render.response_render_abc import (
    ResponseRenderABC,
)


@dataclass
class BodyRender(ResponseRenderABC):
    marshaller: MarshallerABC
    schema: Optional[Schema] = None

    def render(self, kwargs: Dict[str, Any], result: Any) -> Response:
        dumped = self.marshaller.dump(result)
        if self.schema:
            self.schema.validate(dumped)
        return JSONResponse(dumped)

    def to_openapi_schema(
        self, responses: ExternalItemType, components: ExternalItemType, examples: Optional[Tuple[Example, ...]]
    ):
        if not self.schema:
            return
        schema = with_isolated_references(
            self.schema.schema, self.schema.schema, components
        )
        content = {"schema": schema}
        if examples:
            content['examples'] = {
                e.name: filter_none(dict(summary=e.description, value=e.result))
                for e in examples if e.include_in_schema
            }
        responses["200"] = {
            "description": "Successful Response",
            "content": {"application/json": content},
        }
