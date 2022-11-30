from dataclasses import dataclass, field
from typing import Iterator, List

from starlette.routing import Route

from servey.action.finder.action_finder_abc import find_actions_with_trigger_type
from servey.action.finder.found_action import FoundAction
from servey.action.trigger.web_trigger import WebTrigger
from servey.servey_starlette.action_endpoint import ActionEndpoint
from servey.servey_starlette.request_parser.factory.request_parser_factory_abc import (
    create_parser_factories,
    RequestParserFactoryABC,
)
from servey.servey_starlette.request_parser.request_parser_abc import RequestParserABC
from servey.servey_starlette.response_render.factory.response_render_factory_abc import (
    create_render_factories,
    ResponseRenderFactoryABC,
)
from servey.servey_starlette.response_render.response_render_abc import (
    ResponseRenderABC,
)
from servey.servey_starlette.route_factory.route_factory_abc import RouteFactoryABC


@dataclass
class ActionRouteFactory(RouteFactoryABC):
    """Utility for mounting actions to fastapi_integration."""

    parser_factories: List[RequestParserFactoryABC] = field(
        default_factory=create_parser_factories
    )
    render_factories: List[ResponseRenderFactoryABC] = field(
        default_factory=create_render_factories
    )
    path_pattern: str = "/actions/{action_name}"

    def create_routes(self) -> Iterator[Route]:
        for action, trigger in find_actions_with_trigger_type(WebTrigger):
            route = self.create_route(action, trigger)
            yield route

    def create_route(self, action: FoundAction, trigger: WebTrigger) -> Route:
        action_endpoint = self.create_action_endpoint(action, trigger)
        route = action_endpoint.to_route()
        return route

    def create_action_endpoint(
        self, action: FoundAction, trigger: WebTrigger
    ) -> ActionEndpoint:
        parser = self.create_parser(action, trigger)
        render = self.create_render(action)
        endpoint = ActionEndpoint(
            name=action.action_meta.name,
            path=self.path_pattern.format(action_name=action.action_meta.name),
            fn=action.fn,
            methods=(trigger.method,),
            parser=parser,
            render=render,
            description=action.action_meta.description,
        )
        return endpoint

    def create_parser(
        self, action: FoundAction, trigger: WebTrigger
    ) -> RequestParserABC:
        for parser_factory in self.parser_factories:
            parser = parser_factory.create(action, trigger, self.parser_factories)
            if parser:
                return parser

    def create_render(self, action: FoundAction) -> ResponseRenderABC:
        for render_factory in self.render_factories:
            render = render_factory.create(action)
            if render:
                return render
