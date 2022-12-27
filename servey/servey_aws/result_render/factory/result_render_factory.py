from __future__ import annotations

import inspect
import os
from dataclasses import dataclass, field
from typing import Optional, Callable

from marshy import get_default_context
from marshy.marshaller_context import MarshallerContext
from marshy.types import ExternalItemType
from schemey import SchemaContext, get_default_schema_context

from servey.servey_aws.event_parser.event_parser_abc import EventParserABC
from servey.servey_aws.result_render.factory.result_render_factory_abc import (
    ResultRenderFactoryABC,
)
from servey.servey_aws.result_render.result_render import ResultRender
from servey.servey_aws.result_render.result_render_abc import ResultRenderABC


def _get_schema_context():
    if os.environ.get('SERVER_DEBUG') == "1":
        return get_default_schema_context()


@dataclass
class ResultRenderFactory(ResultRenderFactoryABC):
    marshaller_context: MarshallerContext = field(default_factory=get_default_context)
    schema_context: Optional[SchemaContext] = field(default_factory=_get_schema_context)
    priority: int = 50

    def create(
        self, fn: Callable, event: ExternalItemType, context, parser: EventParserABC
    ) -> Optional[ResultRenderABC]:
        sig = inspect.signature(fn)
        marshaller = self.marshaller_context.get_marshaller(sig.return_annotation)
        return ResultRender(marshaller)
