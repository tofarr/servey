import os
from abc import abstractmethod
from dataclasses import dataclass

from mangum import Mangum
from marshy.types import ExternalItemType
from starlette.applications import Starlette

from servey.action import Action
from servey.integration.aws.parser.event_parser_abc import EventParserABC
from servey.integration.aws.render.result_render_abc import ResultRenderABC


@dataclass
class LambdaActionHandler:
    """Adapter which adapts an event to a lambda context (Using mangum for http)"""

    action: Action
    mangum: Mangum
    parser: EventParserABC
    render: ResultRenderABC

    def __call__(self, event, context):
        """Call the action with the event given."""
        if event.get("httpMethod"):
            return self.mangum(event, context)
        else:
            return self.handle_event(event, context)

    def handle_event(self, event: ExternalItemType, context):
        executor, kwargs = self.parser.parse(event, context)
        result = executor.execute(**kwargs)
        rendered = self.render.render(executor, result)
        return rendered
