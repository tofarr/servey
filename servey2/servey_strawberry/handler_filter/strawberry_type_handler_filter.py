from abc import abstractmethod
from inspect import Signature
from typing import Callable, Tuple, Dict, Any

from strawberry.types import Info

from servey.action import Action
from servey.executor import Executor
from servey.integration.strawberry_integration.handler_filter.handler_filter_abc import (
    HandlerFilterABC,
)
from servey.integration.strawberry_integration.schema_factory import SchemaFactory
from servey.trigger.web_trigger import WebTrigger

ExecutorFn = Callable[[Executor, Dict[str, Any]], Any]


class StrawberryTypeHandlerFilter(HandlerFilterABC):
    """
    Sometimes the default behaviour from strawberry is not quite what we want, so this allows us to customize
    how a strawberry object is converted to / from regular python
    Examples include adding authorization
    """

    priority: int = 50

    def filter(
        self,
        action: Action,
        trigger: WebTrigger,
        fn: ExecutorFn,
        sig: Signature,
        schema_factory: SchemaFactory,
    ) -> Tuple[ExecutorFn, Signature, bool]:
        """Filter the action given. The callable is a function"""
        params = [
            p.replace(annotation=schema_factory.get_input(p.annotation))
            for p in sig.parameters.values()
        ]
        sig = sig.replace(
            parameters=params,
            return_annotation=schema_factory.get_type(sig.return_annotation),
        )
        return fn, sig, True
