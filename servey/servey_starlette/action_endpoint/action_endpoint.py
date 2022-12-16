from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Tuple, Any, Optional, Dict

from marshy.marshaller.marshaller_abc import MarshallerABC
from marshy.types import ExternalItemType
from schemey import Schema
from schemey.util import filter_none
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.routing import Route

from servey.action.action import Action
from servey.action.util import with_isolated_references
from servey.servey_starlette.action_endpoint.action_endpoint_abc import (
    ActionEndpointABC,
)
from servey.trigger.web_trigger import WebTriggerMethod, BODY_METHODS


@dataclass
class ActionEndpoint(ActionEndpointABC):
    """
    Wrapper for a function for use within starlette, with everything needed to bind it to a route
    """

    action: Action
    path: str
    methods: Tuple[WebTriggerMethod, ...]
    params_marshaller: MarshallerABC
    params_schema: Optional[Schema]
    result_marshaller: MarshallerABC
    result_schema: Optional[Schema] = None

    def get_action(self) -> Action:
        return self.action

    def get_route(self) -> Route:
        return Route(
            self.path,
            name=self.action.name,
            endpoint=self.execute,
            methods=[m.value for m in self.methods],
        )

    async def execute_with_context(
        self, request: Request, context: Dict[str, Any]
    ) -> Response:
        kwargs = await self.parse_request(request)
        kwargs.update(context)
        result = self.action.fn(**kwargs)
        response = self.render_response(result)
        return response

    async def parse_request(self, request: Request):
        method = WebTriggerMethod(request.method.lower())
        if method in BODY_METHODS:
            body = await request.body()
            params: ExternalItemType = json.loads(body) if body else {}
            error = next(self.params_schema.iter_errors(params), None)
            if error:
                raise HTTPException(422, str(error))
            kwargs = self.params_marshaller.load(params)
        else:
            # All params are strings here, and marshy allows this but schemey does not. so we load before validating,
            # and dump to perform validation
            try:
                kwargs = self.params_marshaller.load(request.query_params)
                params = self.params_marshaller.dump(kwargs)
                self.params_schema.validate(params)
            except:
                raise HTTPException(422, 'invalid_input')
        return kwargs

    def render_response(self, result: Any):
        result_content = self.result_marshaller.dump(result)
        if self.result_schema:
            error = next(self.result_schema.iter_errors(result_content), None)
            if error:
                raise HTTPException(500, str(error))
        return JSONResponse(result_content)

    def to_openapi_schema(self, schema: ExternalItemType):
        paths: ExternalItemType = schema["paths"]
        components: ExternalItemType = schema["components"]
        path = paths.get(self.path)
        if not path:
            path = paths[self.path] = {}
        for method in self.methods:
            responses = {}
            path_method = path[method.value] = {"responses": responses}
            path_method["operationId"] = self.action.name
            if self.action.description:
                path_method["summary"] = self.action.description
            # Tags?
            self.request_to_openapi_schema(method, path_method, components)
            self.response_to_openapi_schema(responses, components)

    def request_to_openapi_schema(
        self,
        method: WebTriggerMethod,
        path_method: ExternalItemType,
        components: ExternalItemType,
    ):
        if method in BODY_METHODS:
            self.body_request_to_openapi_schema(path_method, components)
        else:
            self.query_string_request_to_openapi_schema(path_method, components)

    def body_request_to_openapi_schema(
        self, path_method: ExternalItemType, components: ExternalItemType
    ):
        schema = with_isolated_references(
            self.params_schema.schema, self.params_schema.schema, components
        )
        content = {"schema": schema}
        path_method["requestBody"] = {
            "content": {"application/json": content},
            "required": True,
        }
        if self.action.examples:
            content["examples"] = {
                e.name: filter_none(dict(summary=e.description, value=e.params))
                for e in self.action.examples
                if e.include_in_schema
            }
        responses: ExternalItemType = path_method["responses"]
        responses["422"] = {"description": "Validation Error"}

    def query_string_request_to_openapi_schema(
        self, path_method: ExternalItemType, components: ExternalItemType
    ):
        schema = self.params_schema
        properties = schema.schema["properties"]
        required = set(schema.schema.get("required") or [])
        path_method["parameters"] = [
            filter_none(
                {
                    "required": k in required,
                    "schema": with_isolated_references(schema.schema, v, components),
                    "name": k,
                    "in": "query",
                    "examples": {
                        e.name: filter_none(dict(summary=e.description, value=e.params[k]))
                        for e in self.action.examples if k in e.params
                        if e.include_in_schema
                    }
                    if self.action.examples
                    else None,
                }
            )
            for k, v in properties.items()
        ]
        responses: ExternalItemType = path_method["responses"]
        responses["422"] = {"description": "Validation Error"}

    def response_to_openapi_schema(
        self, responses: ExternalItemType, components: ExternalItemType
    ):
        schema = with_isolated_references(
            self.result_schema.schema, self.result_schema.schema, components
        )
        content = {"schema": schema}
        if self.action.examples:
            content["examples"] = {
                e.name: filter_none(dict(summary=e.description, value=e.result))
                for e in self.action.examples
                if e.include_in_schema
            }
        responses["200"] = {
            "description": "Successful Response",
            "content": {"application/json": content},
        }
