from dataclasses import dataclass
from typing import Dict, Any
from email.utils import parsedate_to_datetime

from marshy.types import ExternalItemType
from schemey import schema_from_type
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from servey.action.action import Action
from servey.servey_starlette.action_endpoint.action_endpoint_abc import (
    ActionEndpointABC,
)
from servey.servey_starlette.error_response import ErrorResponse


@dataclass
class CachingActionEndpoint(ActionEndpointABC):
    """
    Wrapper for an endpoint adding http caching
    """

    action_endpoint: ActionEndpointABC

    def get_action(self) -> Action:
        return self.action_endpoint.get_action()

    def get_route(self) -> Route:
        route = self.action_endpoint.get_route()
        return Route(
            route.path, name=route.name, endpoint=self.execute, methods=route.methods
        )

    async def execute_with_context(
        self, request: Request, context: Dict[str, Any]
    ) -> Response:
        response = await self.action_endpoint.execute_with_context(request, context)
        if response.status_code != 200:
            return response
        # noinspection PyUnresolvedReferences
        cache_header = self.get_action().cache_control.get_cache_header_from_content(
            response.body
        )
        if_match = request.headers.get("If-Match")
        if_modified_since = request.headers.get("If-Modified-Since")
        if if_match and cache_header.etag:
            if cache_header.etag == if_match:
                response = Response(None, 304)
        elif if_modified_since and cache_header.updated_at:
            if_modified_since_date = parsedate_to_datetime(if_modified_since)
            if if_modified_since_date >= cache_header.updated_at:
                response = Response(None, 304)
        response.headers.update(cache_header.get_http_headers())
        return response

    def to_openapi_schema(self, schema: ExternalItemType):
        self.action_endpoint.to_openapi_schema(schema)

        content_error_schema = schema_from_type(ErrorResponse)
        components: Dict = schema["components"]
        components["ErrorResponse"] = content_error_schema.schema

        route = self.action_endpoint.get_route()
        paths: Dict = schema["paths"]
        path: Dict = paths[route.path]
        for method in route.methods:
            # Along with defining the 304 response, do we need to define the etag header, or is this just standard?
            path_method: Dict = path.get(method.lower())
            if path_method is None:
                continue
            responses: Dict = path_method["responses"]
            responses["304"] = {"description": "not_modified", "content": {}}
