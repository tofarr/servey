import os
from typing import Optional, Iterator

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles

from servey.openapi import openapi_schema
from servey.servey_context import ServeyContext, get_default_servey_context
from servey.servey_starlette.starlette_action_handler import StarletteActionHandler

DEFAULT_API_PREFIX = os.environ.get('STARLETTE_API_PREFIX') or '/api'
DEFAULT_WEBSOCKET_PATH = os.environ.get('STARLETTE_WEBSOCKET_PATH') or '/ws'
DEFAULT_OPENAPI_PATH = os.environ.get('STARLETTE_WEBSOCKET_PATH') or '/ws'


def new_default_starlette(servey_context: Optional[ServeyContext] = None,
                          api_prefix: str = DEFAULT_API_PREFIX,
                          debug: bool = True,
                          generate_schemas: bool = True
                          ) -> Starlette:
    starlette = Starlette(debug=debug)
    if servey_context is None:
        servey_context = get_default_servey_context()
    add_action_routes(starlette, servey_context, api_prefix)
    # Add Schema / Other Routes here
    if generate_schemas:
        starlette.routes.append(Route("/openapi.json",
                                      endpoint=openapi_schema_endpoint_factory(servey_context, api_prefix),
                                      include_in_schema=False))
        directory = os.path.dirname(__file__) + '/docs'
        starlette.routes.append(Mount('/docs', app=StaticFiles(directory=directory, html=True)))
    return starlette


def openapi_schema_endpoint_factory(servey_context: ServeyContext, api_prefix: str):
    def endpoint(request: Request):
        content = openapi_schema(servey_context, api_prefix)
        return JSONResponse(content=content)

    return endpoint


def add_action_routes(starlette: Starlette, servey_context: ServeyContext, api_prefix: str):
    starlette.routes.extend(get_action_routes(servey_context, api_prefix))


def get_action_routes(servey_context: ServeyContext, api_prefix: str) -> Iterator[Route]:
    for action in servey_context.actions_by_name.values():
        handler = StarletteActionHandler(action)
        route = Route(
            path=f"{api_prefix}{action.path}",
            endpoint=handler.handle,
            methods=[m.value for m in action.http_methods],
            name=action.name,
            include_in_schema=True,
        )
        yield route
