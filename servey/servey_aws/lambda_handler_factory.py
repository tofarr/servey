from dataclasses import dataclass, field
from typing import Tuple, Iterator

from servey.action.finder.action_finder_abc import find_actions
from servey.action.finder.found_action import FoundAction
from servey.servey_aws.event_parser.event_parser_abc import EventParserABC
from servey.servey_aws.event_parser.factory.event_parser_factory_abc import (
    create_parser_factories,
    EventParserFactoryABC,
)
from servey.servey_aws.lambda_handler import LambdaHandler
from servey.servey_aws.result_render.factory.result_render_factory_abc import (
    ResultRenderFactoryABC,
    create_render_factories,
)
from servey.servey_aws.result_render.result_render_abc import ResultRenderABC


@dataclass
class LambdaHandlerFactory:
    parser_factories: Tuple[EventParserFactoryABC, ...] = field(
        default_factory=create_parser_factories
    )
    render_factories: Tuple[ResultRenderFactoryABC, ...] = field(
        default_factory=create_render_factories
    )

    def create_lambda_handler(self, action: FoundAction) -> LambdaHandler:
        parser = self.create_parser(action)
        render = self.create_render(action)
        return LambdaHandler(action.fn, action.action_meta, parser, render)

    def create_parser(self, action: FoundAction) -> EventParserABC:
        for factory in self.parser_factories:
            parser = factory.create(action, self.parser_factories)
            if parser:
                return parser

    def create_render(self, action: FoundAction) -> ResultRenderABC:
        for factory in self.render_factories:
            render = factory.create(action, self.render_factories)
            if render:
                return render


def create_lambda_handlers() -> Iterator[LambdaHandler]:
    factory = LambdaHandlerFactory()
    for action in find_actions():
        lambda_handler = factory.create_lambda_handler(action)
        yield lambda_handler
