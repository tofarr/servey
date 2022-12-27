import dataclasses
import inspect
from typing import Tuple

from servey.action.action import Action
from servey.servey_strawberry.handler_filter.handler_filter_abc import (
    HandlerFilterABC,
)
from servey.servey_strawberry.schema_factory import SchemaFactory


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
        schema_factory: SchemaFactory,
    ) -> Tuple[Action, bool]:
        fn = action.fn
        sig = inspect.signature(fn)
        params = [
            p.replace(annotation=schema_factory.get_input(p.annotation))
            for p in sig.parameters.values()
        ]
        sig = sig.replace(
            parameters=params,
            return_annotation=schema_factory.get_type(sig.return_annotation),
        )

        def resolver(*args, **kwargs):
            # Should we unwrap strawberry inputs here?
            result = fn(*args, **kwargs)
            # Should we wrap the result type here?
            return result

        resolver.__signature__ = sig
        wrapped_action = dataclasses.replace(action, fn=resolver)

        return wrapped_action, True
