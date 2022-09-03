import inspect
from dataclasses import dataclass, field, is_dataclass, fields
from typing import Tuple, Optional

from marshy.factory.optional_marshaller_factory import get_optional_type

from servey2.action.finder.found_action import FoundAction
from servey2.action.trigger.web_trigger import WebTrigger
from servey2.security.access_control.allow_all import ALLOW_ALL
from servey2.security.authorization import Authorization
from servey2.security.authorizer.authorizer_abc import AuthorizerABC
from servey2.security.authorizer.authorizer_factory_abc import get_default_authorizer
from servey2.servey_starlette.request_parser.authorizing_parser import AuthorizingParser
from servey2.servey_starlette.request_parser.factory.request_parser_factory_abc import (
    RequestParserFactoryABC,
)
from servey2.servey_starlette.request_parser.factory.self_parser_factory import strip_injected_from_action
from servey2.servey_starlette.request_parser.request_parser_abc import RequestParserABC


@dataclass
class AuthorizingParserFactory(RequestParserFactoryABC):
    priority: int = 80
    authorizer: AuthorizerABC = field(default_factory=get_default_authorizer)
    skip: bool = False

    def create(
        self,
        action: FoundAction,
        trigger: WebTrigger,
        parser_factories: Tuple[RequestParserFactoryABC],
    ) -> Optional[RequestParserABC]:
        if self.skip:
            return
        inject_at = get_inject_at(action)
        if (
            action.action_meta.access_control == ALLOW_ALL
            and not inject_at
        ):
            return
        wrapped_action = action
        if inject_at:
            # If the wrapped parser tries to invoke the function we supply no authorization
            wrapped_action = strip_injected_from_action(action, inject_at, lambda: None)

        self.skip = True
        try:
            for factory in parser_factories:
                parser = factory.create(wrapped_action, trigger, parser_factories)
                if parser:
                    return AuthorizingParser(
                        self.authorizer, parser, inject_at, action.action_meta.access_control
                    )
        finally:
            self.skip = False


def get_inject_at(action: FoundAction) -> Optional[str]:
    sig = inspect.signature(action.fn)
    for p in sig.parameters.values():
        annotation = get_optional_type(p.annotation) or p.annotation
        if annotation == Authorization:
            return p.name
        if is_dataclass(annotation):
            for f in fields(annotation):
                annotation = get_optional_type(f.type) or p.annotation
                if annotation == Authorization:
                    return f"{p.name}.{f.name}"
