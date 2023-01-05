from dataclasses import dataclass
from typing import Type

from marshy.types import ExternalItemType

from servey.security.access_control.allow_all import ALLOW_ALL
from servey.security.authorization import AuthorizationError
from servey.servey_aws.event_handler.event_handler import (
    EventHandler,
    EventHandlerFactory,
)
from servey.servey_aws.event_handler.event_handler_abc import EventHandlerABC


class AppsyncEventHandler(EventHandler):
    def is_usable(self, event: ExternalItemType, context) -> bool:
        return "arguments" in event

    def parse_kwargs(self, event: ExternalItemType):
        arguments = dict(**event["arguments"])
        source = event.get("source")
        if source is not None:
            arguments["self"] = source
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


@dataclass
class AppsyncEventHandlerFactory(EventHandlerFactory):
    priority: int = 100
    event_handler_type: Type[EventHandlerABC] = AppsyncEventHandler
