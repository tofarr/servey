from dataclasses import dataclass, field
from typing import Optional, Iterator, List

from starlette.routing import Route

from servey.action import Action
from servey.action_context import get_default_action_context, ActionContext
from servey.integration.starlette_integ.action_route import ActionRoute

from servey.integration.starlette_integ.parser.parser_abc import (
    create_parser_factories,
    ParserFactoryABC,
    ParserABC,
)
from servey.integration.starlette_integ.render.render_abc import (
    create_render_factories,
    RenderFactoryABC,
    RenderABC,
)
from servey.integration.starlette_integ.route_factory.route_factory_abc import (
    RouteFactoryABC,
)
from servey.trigger.web_trigger import WebTrigger


@dataclass
class ActionRouteFactory(RouteFactoryABC):
    """Utility for mounting actions to fastapi_integration."""

    parser_factories: List[ParserFactoryABC] = field(
        default_factory=create_parser_factories
    )
    render_factories: List[RenderFactoryABC] = field(
        default_factory=create_render_factories
    )
    path_pattern: str = "/actions/{action_name}"

    def create_routes(
        self, action_context: Optional[ActionContext] = None
    ) -> Iterator[Route]:
        if not action_context:
            action_context = get_default_action_context()
        for action_route in self.create_action_routes(action_context):
            route = action_route.to_route()
            yield route

    def create_action_routes(
        self, action_context: ActionContext
    ) -> Iterator[ActionRoute]:
        for action, trigger in action_context.get_actions_with_trigger_type(WebTrigger):
            action_route = self.create_action_route(action, trigger)
            yield action_route

    def create_action_route(self, action: Action, trigger: WebTrigger) -> ActionRoute:
        parser = self.create_parser_for_action(action, trigger)
        render = self.create_render_for_action(action)

        action_route = ActionRoute(
            action=action,
            path=self.path_pattern.format(action_name=action.action_meta.name),
            methods=(trigger.method,),
            parser=parser,
            render=render,
        )
        return action_route

    def create_parser_for_action(
        self, action: Action, trigger: WebTrigger
    ) -> ParserABC:
        for factory in self.parser_factories:
            parser = factory.create(action, trigger, self.parser_factories)
            if parser:
                return parser

    def create_render_for_action(self, action: Action) -> RenderABC:
        for factory in self.render_factories:
            render = factory.create(action)
            if render:
                return render
