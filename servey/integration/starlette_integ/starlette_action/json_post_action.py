from dataclasses import dataclass
from typing import Any, Tuple, Dict
from uuid import uuid4

from marshy.types import ExternalItemType
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from servey.action import Action
from servey.executor import Executor
from servey.integration.starlette_integ.starlette_action.action_route_abc import (
    ActionRouteABC,
)
from servey.trigger.web_trigger import WebTriggerMethod

LOGGER = getLogger(__name__)


@dataclass
class JsonPostAction(ActionRouteABC):
    action: Action
    path: str
    method: WebTriggerMethod

    def get_action(self) -> Action:
        return self.action

    def get_route(self) -> Route:
        return Route(self.path, endpoint=self.execute, methods=[self.method.value()])

    def get_openapi_schema(self) -> ExternalItemType:
        action_meta = self.action.action_meta
        return {
            self.method.value: {
                "summary": action_meta.description,
                "operationId": action_meta.name,
                "requestBody": {
                    "content": {
                        "application/json": {"schema": action_meta.params_schema.schema}
                    },
                    "required": True,
                },
                "responses": {
                    "200": {
                        "description": "Success",
                        "application/json": {
                            "schema": action_meta.result_schema.schema
                        },
                    }
                },
            }
        }

    async def parse(self, request: Request) -> Tuple[Executor, Dict[str, Any]]:
        params = await self.parse_params(request)
        action_meta = self.action.action_meta
        action_meta.params_schema.validate(params)
        marshalled = action_meta.params_marshaller.load(params)
        return marshalled

    async def parse_params(self, request: Request) -> ExternalItemType:
        content_type = request.headers.get("Content-Type") or ""
        if content_type and not content_type.lower().startswith("application/json"):
            raise HTTPException(400)
        params = await request.json()
        return params

    def render(self, executor: Executor, result: Any) -> JSONResponse:
        action_meta = self.action.action_meta
        dumped = action_meta.result_marshaller.dump(result)
        action_meta.result_schema.validate(dumped)  # This may throw a 500 error
        return JSONResponse(dumped)
