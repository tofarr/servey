import inspect
from dataclasses import dataclass, replace
from logging import getLogger
from typing import Optional, Callable, List

from servey.action.finder.found_action import FoundAction
from servey.action.trigger.web_trigger import WebTrigger
from servey.servey_starlette.request_parser.factory.request_parser_factory_abc import (
    RequestParserFactoryABC,
)
from servey.servey_starlette.request_parser.request_parser_abc import RequestParserABC
from servey.servey_starlette.request_parser.self_parser import SelfParser
from servey.action.util import (
    strip_injected_from_schema,
    wrap_fn_for_injection,
)

LOGGER = getLogger(__name__)


@dataclass
class SelfParserFactory(RequestParserFactoryABC):
    priority: int = 90
    skip: bool = False

    def create(
        self,
        action: FoundAction,
        trigger: WebTrigger,
        parser_factories: List[RequestParserFactoryABC],
    ) -> Optional[RequestParserABC]:
        if self.skip or not action.owner:
            return
        sig = inspect.signature(action.fn)
        if not sig.parameters:
            LOGGER.warning(f"Missing 'self' parameter for {action.fn.__name__}")
            return
        self_name = next(sig.parameters)
        wrapped_action = strip_injected_from_action(action, self_name, action.owner)
        self.skip = True
        try:
            for f in parser_factories:
                parser = f.create(wrapped_action, trigger, parser_factories)
                if parser:
                    return SelfParser(parser, action.owner, self_name)
        finally:
            self.skip = False


def strip_injected_from_action(
    action: FoundAction, inject_at: str, constructor: Callable
) -> FoundAction:
    """
    Create a version of the action given where the injected argument given is stripped out,
    effectively behaving as if it does not exist
    """
    action = FoundAction(
        fn=wrap_fn_for_injection(action.fn, inject_at, constructor),
        action_meta=replace(
            action.action_meta,
            params_schema=strip_injected_from_schema(
                action.action_meta.params_schema, inject_at
            ),
        ),
    )
    return action
