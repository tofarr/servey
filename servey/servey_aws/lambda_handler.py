from dataclasses import dataclass
from typing import Callable

from marshy.types import ExternalItemType

from servey.action.action_meta import ActionMeta
from servey.servey_aws.event_parser.event_parser_abc import EventParserABC
from servey.servey_aws.result_render.result_render_abc import ResultRenderABC


@dataclass
class LambdaHandler:
    fn: Callable
    action_meta: ActionMeta
    event_parser: EventParserABC
    result_render: ResultRenderABC

    def __call__(self, event: ExternalItemType, context):
        kwargs = self.event_parser.parse(event, context)
        result = self.fn(**kwargs)
        rendered = self.result_render.render_result(result)
        return rendered
