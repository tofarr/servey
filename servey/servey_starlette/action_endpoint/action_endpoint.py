from __future__ import annotations
import json
import logging
from dataclasses import dataclass
from string import Formatter
from typing import Tuple, Any, Optional, Dict, List, Iterator, Awaitable

from json_urley import query_str_to_json_obj
from marshy.marshaller.marshaller_abc import MarshallerABC
from marshy.types import ExternalItemType
from schemey import Schema
from schemey.util import filter_none
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.routing import Route

from servey.action.action import Action
from servey.action.example import Example
from servey.action.util import move_ref_items_to_components
from servey.servey_starlette.action_endpoint.action_endpoint_abc import (
    ActionEndpointABC,
)
from servey.trigger.web_trigger import WebTriggerMethod, BODY_METHODS

LOGGER = logging.getLogger(__name__)


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

    def __post_init__(self):
        self.field_names = {
            fname for _, fname, _, _ in Formatter().parse(self.path) if fname
        }

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
        if isinstance(result, Awaitable):
            result = await result
        # Lazy action resolution would be done here!
        response = self.render_response(result)
        return response

    async def parse_request(self, request: Request):
        method = WebTriggerMethod(request.method.lower())
        if method in BODY_METHODS:
            body = await request.body()
            params: ExternalItemType = json.loads(body) if body else {}
            if request.path_params:
                params.update(request.path_params)
            error = next(self.params_schema.iter_errors(params), None)
            if error:
                raise HTTPException(422, str(error))
            kwargs = self.params_marshaller.load(params)
        else:
            try:
                query_str = request.scope["query_string"] or b""
                if isinstance(query_str, bytes):
                    query_str = query_str.decode("latin-1")
                json_obj = query_str_to_json_obj(query_str)
                if request.path_params:
                    json_obj.update(request.path_params)
                self.params_schema.validate(json_obj)
                kwargs = self.params_marshaller.load(json_obj)
            except Exception:
                LOGGER.exception("invalid_input")
                raise HTTPException(422, "invalid_input")
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
            self.query_string_request_to_openapi_schema(path_method)

    def body_request_to_openapi_schema(
        self, path_method: ExternalItemType, components: ExternalItemType
    ):
        schema = move_ref_items_to_components(
            self.params_schema.schema, self.params_schema.schema, components
        )

        if self.field_names:
            parameters = []
            properties = schema.get("properties")
            required_properties = schema.get("required") or []
            for field_name in self.field_names:
                parameters.append(
                    {
                        "required": field_name in required_properties,
                        "schema": properties.pop(field_name),
                        "name": field_name,
                        "in": "path",
                    }
                )
                if field_name in required_properties:
                    required_properties.remove(field_name)
            path_method["parameters"] = parameters

        # move params from schema to params if path params
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

    def query_string_request_to_openapi_schema(self, path_method: ExternalItemType):
        # Schema to openapi
        params = list(
            _object_schema_to_json_urley_parameters(
                object_schema=self.params_schema.schema,
                examples=self.action.examples or tuple(),
                path=[],
            )
        )
        if self.field_names:
            for param in params:
                if param["name"] in self.field_names:
                    param["in"] = "path"
        path_method["parameters"] = params
        responses: ExternalItemType = path_method["responses"]
        responses["422"] = {"description": "Validation Error"}

    def response_to_openapi_schema(
        self, responses: ExternalItemType, components: ExternalItemType
    ):
        schema = self.result_schema.schema
        schema = move_ref_items_to_components(schema, schema, components)
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


def _object_schema_to_json_urley_parameters(
    object_schema: ExternalItemType, examples: Tuple[Example], path: List[str]
) -> Iterator[ExternalItemType]:
    """
    This is not full support for json urley - parameters with references / urls are ignored and just do not appear
    in the schema.
    """
    properties: ExternalItemType = object_schema.get("properties")
    required_properties = set(object_schema.get("required") or [])
    for key, property_schema in properties.items():
        valid_schema = _get_valid_openapi_param_schema(property_schema)
        if not valid_schema:
            continue
        path.append(key.replace("~", "~~").replace(".", "~."))
        valid_schema = _get_nullable_schema(valid_schema) or valid_schema
        if valid_schema.get("type") == "object":
            yield from _object_schema_to_json_urley_parameters(
                valid_schema, examples, path
            )
        else:
            example_schemas = {}
            for example in examples:
                example_value = example.params
                for p in path:
                    example_value = example_value.get(p, None)
                    if example_value is None:
                        break
                if example_value is not None:
                    example_schema = dict(value=example_value)
                    if example.description:
                        example_schema["summary"] = example.description
                    example_schemas[example.name] = example_schema

            result = {
                "required": key in required_properties,
                "schema": property_schema,
                "name": ".".join(path),
                "in": "query",
            }
            if example_schemas:
                result["examples"] = example_schemas
            yield result
        path.pop()


def _get_valid_openapi_param_schema(schema: ExternalItemType):
    nullable_schema = _get_nullable_schema(schema)
    if nullable_schema:
        sub_schema = _get_valid_openapi_param_schema(nullable_schema)
        return nullable_schema if sub_schema else None
    type_ = schema.get("type")
    if not type_:
        return
    type_ = type_.lower()
    if type_ == "array":
        sub_schema: ExternalItemType = schema.get("items")
        if not sub_schema:
            return
        sub_schema = _get_nullable_schema(sub_schema) or sub_schema
        type_ = sub_schema.get("type")
        if type_ in ("boolean", "number", "integer", "string", "null"):
            # We currently don't support nested arrays of objects / arrays in an openapi schema
            return schema
    elif type_ in ("boolean", "number", "integer", "object", "string"):
        return schema


def _get_nullable_schema(schema: ExternalItemType):
    any_of = schema.get("anyOf")
    if any_of:
        if not isinstance(any_of, list):
            return
        non_nulls = [s for s in any_of if s.get("type") != "null"]
        if len(non_nulls) != 1:
            return
        return non_nulls[0]
