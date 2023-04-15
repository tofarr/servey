from dataclasses import dataclass
from typing import Type, Any

from marshy.types import ExternalItemType, ExternalType

from servey.security.access_control.allow_all import ALLOW_ALL
from servey.security.authorization import AuthorizationError
from servey.servey_aws.event_handler.event_handler import (
    EventHandler,
    EventHandlerFactory,
)
from servey.servey_aws.event_handler.event_handler_abc import EventHandlerABC
from servey.util import to_snake_case, attr_camel_case


class AppsyncEventHandler(EventHandler):
    def is_usable(self, event: ExternalItemType, context) -> bool:
        return "arguments" in event

    def parse_kwargs(self, event: ExternalItemType):
        arguments = dict(**event["arguments"])
        source = event.get("source")
        if source is not None:
            arguments["self"] = source
        arguments = attrs_to_snake_case(arguments)
        if self.param_schema:
            self.param_schema.validate(arguments)
        kwargs = self.param_marshaller.load(arguments)
        if self.auth_kwarg_name or self.action.access_control != ALLOW_ALL:
            # noinspection PyTypeChecker
            headers: ExternalItemType = (event.get("request") or {}).get(
                "headers"
            ) or {}
            auth_header = headers.get("authorization")
            authorization = None
            if auth_header:
                if auth_header.lower().startswith("bearer "):
                    auth_header = auth_header[7:]
                authorization = self.authorizer.authorize(auth_header)
            if not self.action.access_control.is_executable(authorization):
                raise AuthorizationError("unauthorized")
            if self.auth_kwarg_name:
                kwargs[self.auth_kwarg_name] = authorization
        return kwargs

    def render_result(self, result: Any) -> ExternalType:
        result = super().render_result(result)
        result = attrs_to_camel_case(result)
        return result


@dataclass
class AppsyncEventHandlerFactory(EventHandlerFactory):
    priority: int = 100
    event_handler_type: Type[EventHandlerABC] = AppsyncEventHandler


def attrs_to_snake_case(arguments: ExternalType) -> ExternalType:
    if isinstance(arguments, dict):
        result = {
            to_snake_case(k): attrs_to_snake_case(v)
            for k, v in arguments.items()
        }
        return result
    elif isinstance(arguments, list):
        result = [
            attrs_to_snake_case(a)
            for a in arguments
        ]
        return result
    else:
        return arguments


def attrs_to_camel_case(result: ExternalType) -> ExternalType:
    if isinstance(result, dict):
        result = {
            attr_camel_case(k): attrs_to_camel_case(v)
            for k, v in result.items()
        }
        return result
    elif isinstance(result, list):
        result = [
            attrs_to_camel_case(a)
            for a in result
        ]
        return result
    else:
        return result
