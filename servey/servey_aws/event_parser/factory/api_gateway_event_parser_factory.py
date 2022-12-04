from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Callable

from marshy import get_default_context
from marshy.marshaller_context import MarshallerContext
from marshy.types import ExternalItemType
from schemey import SchemaContext, get_default_schema_context

from servey.action.action import get_marshaller_for_params
from servey.security.authorization import Authorization
from servey.security.authorizer.authorizer_factory_abc import create_authorizer
from servey.servey_aws.event_parser.api_gateway_event_parser import (
    ApiGatewayEventParser,
)
from servey.servey_aws.event_parser.event_parser_abc import EventParserABC
from servey.servey_aws.event_parser.factory.event_parser_factory import (
    separate_auth_kwarg,
)
from servey.servey_aws.event_parser.factory.event_parser_factory_abc import (
    EventParserFactoryABC,
)


@dataclass
class ApiGatewayEventParserFactory(EventParserFactoryABC):
    marshaller_context: MarshallerContext = field(default_factory=get_default_context)
    schema_context: SchemaContext = field(default_factory=get_default_schema_context)
    priority: int = 100

    def create(
        self, fn: Callable, event: ExternalItemType, context
    ) -> Optional[EventParserABC]:
        if "httpMethod" not in event:
            return
        fn, auth_kwarg_name = separate_auth_kwarg(fn)
        authorizer = None
        if auth_kwarg_name:
            authorizer = create_authorizer()
        marshaller = get_marshaller_for_params(fn, self.marshaller_context)
        return ApiGatewayEventParser(marshaller, auth_kwarg_name, authorizer)
