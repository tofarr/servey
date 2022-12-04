from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Optional, Callable, Tuple

from marshy import get_default_context
from marshy.marshaller_context import MarshallerContext
from marshy.types import ExternalItemType
from schemey import get_default_schema_context, SchemaContext

from servey.action.action import get_marshaller_for_params
from servey.security.authorization import Authorization
from servey.security.authorizer.authorizer_factory_abc import create_authorizer
from servey.security.util import get_inject_at
from servey.servey_aws.event_parser.event_parser import EventParser
from servey.servey_aws.event_parser.event_parser_abc import EventParserABC
from servey.servey_aws.event_parser.factory.event_parser_factory_abc import (
    EventParserFactoryABC,
)


@dataclass
class EventParserFactory(EventParserFactoryABC):
    marshaller_context: MarshallerContext = field(default_factory=get_default_context)
    schema_context: SchemaContext = field(default_factory=get_default_schema_context)
    validate: bool = True
    allow_unsigned_auth: bool = True
    priority: int = 50

    def create(
        self, fn: Callable, event: ExternalItemType, context
    ) -> Optional[EventParserABC]:
        fn, auth_kwarg_name = separate_auth_kwarg(fn)
        authorizer = None
        auth_marshaller = None
        if auth_kwarg_name:
            authorizer = create_authorizer()
            if self.allow_unsigned_auth:
                auth_marshaller = self.marshaller_context.get_marshaller(Authorization)
        marshaller = get_marshaller_for_params(fn, self.marshaller_context)
        # noinspection PyUnresolvedReferences
        schema = (
            get_schema_for_params(fn, self.schema_context) if self.validate else None
        )
        return EventParser(
            marshaller, schema, auth_kwarg_name, authorizer, auth_marshaller
        )


def separate_auth_kwarg(fn: Callable) -> Tuple[Callable, Optional[str]]:
    attr_name = get_inject_at(fn)
    if not attr_name:
        return fn, attr_name

    def noop(**kwargs):
        # This function exists to transfer signature data. it is never called
        raise ValueError()

    sig = inspect.signature(fn)
    sig = sig.replace(
        parameters=[p for p in sig.parameters.values() if p.name != attr_name]
    )
    noop.__signature__ = sig

    return noop, attr_name
