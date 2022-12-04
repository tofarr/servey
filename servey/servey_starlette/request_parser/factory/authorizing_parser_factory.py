from dataclasses import dataclass, field
from typing import List, Optional


from servey.action.finder.found_action import FoundAction
from servey.action.trigger.web_trigger import WebTrigger
from servey.security.access_control.allow_all import ALLOW_ALL
from servey.security.authorizer.authorizer_abc import AuthorizerABC
from servey.security.authorizer.authorizer_factory_abc import get_default_authorizer
from servey.security.util import get_inject_at
from servey.servey_starlette.request_parser.authorizing_parser import AuthorizingParser
from servey.servey_starlette.request_parser.factory.request_parser_factory_abc import (
    RequestParserFactoryABC,
)
from servey.servey_starlette.request_parser.factory.self_parser_factory import (
    strip_injected_from_action,
)
from servey.servey_starlette.request_parser.request_parser_abc import RequestParserABC


@dataclass
class AuthorizingParserFactory(RequestParserFactoryABC):
    priority: int = 80
    authorizer: AuthorizerABC = field(default_factory=get_default_authorizer)
    skip: bool = False

    def create(
        self,
        action: FoundAction,
        trigger: WebTrigger,
        parser_factories: List[RequestParserFactoryABC],
    ) -> Optional[RequestParserABC]:
        if self.skip:
            return
        inject_at = get_inject_at(action.fn)
        if action.action_meta.access_control == ALLOW_ALL and not inject_at:
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
                        self.authorizer,
                        parser,
                        inject_at,
                        action.action_meta.access_control,
                    )
        finally:
            self.skip = False
