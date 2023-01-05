import inspect
import json
from dataclasses import field, dataclass
from typing import Optional

from marshy import get_default_context, ExternalType
from marshy.marshaller.marshaller_abc import MarshallerABC
from marshy.marshaller_context import MarshallerContext
from marshy.types import ExternalItemType
from schemey import get_default_schema_context, SchemaContext, Schema

from servey.action.action import Action
from servey.servey_aws.event_handler.event_handler_abc import (
    EventHandlerABC,
    EventHandlerFactoryABC,
)


@dataclass
class SqsEventHandler(EventHandlerABC):
    action: Action
    event_marshaller: MarshallerABC
    event_schema: Optional[Schema]
    result_marshaller: MarshallerABC
    priority: int = 50

    def is_usable(self, event: ExternalItemType, context) -> bool:
        return "Records" in event

    def handle(self, event: ExternalItemType, context) -> ExternalType:
        # noinspection PyTypeChecker
        records = [json.loads(r["body"]) for r in event["Records"]]
        if self.event_schema:
            for r in records:
                self.event_schema.validate(r)
        arg_list = [self.event_marshaller.load(r) for r in records]
        if self.action.batch_invoker:
            results = self.action.batch_invoker.fn(arg_list)
        else:
            results = [self.action.fn(a) for a in arg_list]
        if self.result_marshaller:
            results = [self.result_marshaller.dump(r) for r in results]
        return results


@dataclass
class SqsEventHandlerFactory(EventHandlerFactoryABC):
    marshaller_context: MarshallerContext = field(default_factory=get_default_context)
    schema_context: SchemaContext = field(default_factory=get_default_schema_context)
    priority: int = 100

    def create(self, action: Action) -> Optional[EventHandlerABC]:
        sig = inspect.signature(action.fn)
        params = list(sig.parameters.values())
        if len(params) != 1:
            return  # Sqs requires a single event
        event_type = params[0].annotation
        event_schema = self.schema_context.schema_from_type(event_type)
        event_marshaller = self.marshaller_context.get_marshaller(event_type)
        result_marshaller = None
        if sig.return_annotation != inspect.Signature.empty:
            result_marshaller = self.marshaller_context.get_marshaller(
                sig.return_annotation
            )
        return SqsEventHandler(
            action=action,
            event_marshaller=event_marshaller,
            event_schema=event_schema,
            result_marshaller=result_marshaller,
            priority=self.priority,
        )
