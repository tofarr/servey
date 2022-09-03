from dataclasses import field
from typing import Tuple, Optional

from marshy import get_default_context
from marshy.marshaller_context import MarshallerContext

from servey.integration.starlette_integ.parser.parser_abc import ParserFactoryABC
from servey.action.finder.found_action import FoundAction
from servey.action.trigger.web_trigger import WebTrigger, BODY_METHODS
from servey.servey_starlette.request_parser.factory.body_parser_factory import get_marshaller_for_params
from servey.servey_starlette.request_parser.query_string_parser import QueryStringParser
from servey.servey_starlette.request_parser.request_parser_abc import RequestParserABC


class QueryStringParserFactory(ParserFactoryABC):
    marshaller_context: MarshallerContext = field(default_factory=get_default_context)
    priority: int = 50

    def create(
        self,
        action: FoundAction,
        trigger: WebTrigger,
        parser_factories: Tuple[ParserFactoryABC],
    ) -> Optional[RequestParserABC]:
        if trigger.method not in BODY_METHODS:
            return QueryStringParser(
                schema=action.action_meta.params_schema,
                marshaller=get_marshaller_for_params(action.fn, self.marshaller_context)
            )
