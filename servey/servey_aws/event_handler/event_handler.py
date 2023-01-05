import asyncio
import inspect
from dataclasses import field, dataclass
from typing import Optional, Tuple, Callable, Any, Type, Awaitable

from marshy import get_default_context, ExternalType
from marshy.marshaller.marshaller_abc import MarshallerABC
from marshy.marshaller_context import MarshallerContext
from marshy.types import ExternalItemType
from schemey import get_default_schema_context, SchemaContext, Schema

from servey.action.action import Action
from servey.action.util import get_marshaller_for_params, get_schema_for_params
from servey.security.access_control.allow_all import ALLOW_ALL
from servey.security.authorization import (
    Authorization,
    get_inject_at,
    AuthorizationError,
)
from servey.security.authorizer.authorizer_abc import AuthorizerABC
from servey.security.authorizer.authorizer_factory_abc import get_default_authorizer
from servey.servey_aws.event_handler.event_handler_abc import (
    EventHandlerABC,
    EventHandlerFactoryABC,
)


@dataclass
class EventHandler(EventHandlerABC):
    action: Action
    param_marshaller: MarshallerABC
    param_schema: Optional[Schema]
    result_marshaller: Optional[MarshallerABC]
    result_schema: Optional[Schema] = None
    auth_kwarg_name: Optional[str] = None
    auth_marshaller: Optional[MarshallerABC[Authorization]] = None
    authorizer: Optional[AuthorizerABC] = None
    priority: int = 50

    def is_usable(self, event: ExternalItemType, context) -> bool:
        return "params" in event

    def handle(self, event: ExternalItemType, context) -> ExternalType:
        kwargs = self.parse_kwargs(event)
        result = self.action.fn(**kwargs)
        if isinstance(result, Awaitable):
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(result)
        return self.render_result(result)

    def parse_kwargs(self, event: ExternalItemType):
        params = event["params"]
        if self.param_schema:
            self.param_schema.validate(params)
        kwargs = self.param_marshaller.load(params)
        if self.action.access_control != ALLOW_ALL or self.auth_kwarg_name:
            auth_kwarg_value = event.get("authorization")
            authorization = None
            if isinstance(auth_kwarg_value, str):
                authorization = self.authorizer.authorize(auth_kwarg_value)
            elif isinstance(auth_kwarg_value, dict):
                authorization = self.auth_marshaller.load(auth_kwarg_value)
            if not self.action.access_control.is_executable(authorization):
                raise AuthorizationError("unauthorized")
            if self.auth_kwarg_name:
                kwargs[self.auth_kwarg_name] = authorization
        return kwargs

    def render_result(self, result: Any) -> ExternalType:
        if self.result_marshaller:
            result = self.result_marshaller.dump(result)
        if self.result_schema:
            self.result_schema.validate(result)
        return result


@dataclass
class EventHandlerFactory(EventHandlerFactoryABC):
    marshaller_context: MarshallerContext = field(default_factory=get_default_context)
    schema_context: SchemaContext = field(default_factory=get_default_schema_context)
    validate_output: bool = True
    allow_unsigned_auth: bool = True
    priority: int = 50
    event_handler_type: Type[EventHandlerABC] = EventHandler

    def create(self, action: Action) -> EventHandlerABC:
        fn, auth_kwarg_name = separate_auth_kwarg(action.fn)
        authorizer = None
        auth_marshaller = None
        if auth_kwarg_name or action.access_control != ALLOW_ALL:
            authorizer = get_default_authorizer()
            if self.allow_unsigned_auth:
                auth_marshaller = self.marshaller_context.get_marshaller(Authorization)
        param_marshaller = get_marshaller_for_params(fn, set(), self.marshaller_context)
        param_schema = get_schema_for_params(fn, set(), self.schema_context)
        sig = inspect.signature(fn)
        result_marshaller = None
        result_schema = None
        if sig.return_annotation != inspect.Signature.empty:
            result_marshaller = self.marshaller_context.get_marshaller(
                sig.return_annotation
            )
            if self.validate_output:
                result_schema = self.schema_context.schema_from_type(
                    sig.return_annotation
                )
        return self.event_handler_type(
            action=action,
            param_marshaller=param_marshaller,
            param_schema=param_schema,
            result_marshaller=result_marshaller,
            result_schema=result_schema,
            auth_kwarg_name=auth_kwarg_name,
            auth_marshaller=auth_marshaller,
            authorizer=authorizer,
            priority=self.priority,
        )


def separate_auth_kwarg(fn: Callable) -> Tuple[Callable, Optional[str]]:
    attr_name = get_inject_at(fn)
    if not attr_name:
        return fn, attr_name

    def noop(**_):
        """This function exists to transfer signature data. it is never called"""

    sig = inspect.signature(fn)
    sig = sig.replace(
        parameters=[p for p in sig.parameters.values() if p.name != attr_name]
    )
    noop.__signature__ = sig

    return noop, attr_name
