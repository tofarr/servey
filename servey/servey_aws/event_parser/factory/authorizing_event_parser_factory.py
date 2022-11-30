from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, Optional

from servey.action.finder.found_action import FoundAction
from servey.security.access_control.allow_all import ALLOW_ALL
from servey.security.authorizer.authorizer_abc import AuthorizerABC
from servey.security.authorizer.authorizer_factory_abc import get_default_authorizer
from servey.servey_aws.event_parser.authorizing_event_parser import (
    AuthorizingEventParser,
)
from servey.servey_aws.event_parser.event_parser_abc import EventParserABC
from servey.servey_aws.event_parser.factory.event_parser_factory_abc import (
    EventParserFactoryABC,
)
from servey.servey_starlette.request_parser.factory.authorizing_parser_factory import (
    get_inject_at,
)


@dataclass
class AuthorizingEventParserFactory(EventParserFactoryABC):
    authorizer: AuthorizerABC = field(default_factory=get_default_authorizer)
    priority: int = 80
    skip: bool = False

    def create(
        self, action: FoundAction, factories: Tuple[EventParserFactoryABC, ...]
    ) -> Optional[EventParserABC]:
        if self.skip:
            return
        inject_at = get_inject_at(action)
        if action.action_meta.access_control == ALLOW_ALL and not inject_at:
            return
        wrapped_action = action
        if inject_at:
            # If the wrapped parser tries to invoke the function we supply no authorization
            wrapped_action = strip_injected_from_action(action, inject_at, lambda: None)

        self.skip = True
        try:
            for factory in factories:
                parser = factory.create(wrapped_action, factories)
                if parser:
                    return AuthorizingEventParser(
                        parser,
                        self.authorizer,
                        inject_at,
                        action.action_meta.access_control,
                    )
        finally:
            self.skip = False
