from dataclasses import dataclass
from typing import Any, Optional, List

from marshy.types import ExternalItemType
from requests import Response
from starlette.responses import JSONResponse

from servey.action import Action
from servey.executor import Executor
from servey.integration.starlette_integ.render.render_abc import (
    RenderABC,
    RenderFactoryABC,
)
from servey.integration.starlette_integ.util import with_isolated_references


@dataclass
class BodyRender(RenderABC):
    action: Action

    def render(self, executor: Executor, result: Any) -> JSONResponse:
        action_meta = self.action.action_meta
        dumped = action_meta.result_marshaller.dump(result)
        # Should we really validate all output? That sounds like a you problem!
        action_meta.result_schema.validate(dumped)
        return JSONResponse(dumped)

    def to_openapi_schema(
        self, responses: ExternalItemType, components: ExternalItemType
    ):
        schema = self.action.action_meta.result_schema
        schema = with_isolated_references(schema.schema, schema.schema, components)
        responses["200"] = {
            "description": "Successful Response",
            "content": {"application/json": {"schema": schema}},
        }


class BodyRenderFactory(RenderFactoryABC):
    priority: int = 50

    def create(self, action: Action) -> Optional[RenderABC]:
        return BodyRender(action)
