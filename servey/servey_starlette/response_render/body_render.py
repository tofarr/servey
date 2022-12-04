from dataclasses import dataclass
from typing import Any, Optional, Dict

from marshy.marshaller.marshaller_abc import MarshallerABC
from marshy.types import ExternalItemType
from schemey import Schema
from starlette.responses import JSONResponse, Response

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
        self, responses: ExternalItemType, components: ExternalItemType
    ):
        if not self.schema:
            return
        schema = with_isolated_references(
            self.schema.schema, self.schema.schema, components
        )
        responses["200"] = {
            "description": "Successful Response",
            "content": {"application/json": {"schema": schema}},
        }
