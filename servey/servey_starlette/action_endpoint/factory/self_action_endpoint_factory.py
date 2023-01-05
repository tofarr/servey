import dataclasses
import importlib
import inspect
from dataclasses import dataclass
from typing import List, Optional, Set

from servey.action.action import Action
from servey.servey_starlette.action_endpoint.action_endpoint_abc import (
    ActionEndpointABC,
)
from servey.servey_starlette.action_endpoint.factory.action_endpoint_factory_abc import (
    ActionEndpointFactoryABC,
)


@dataclass
class SelfActionEndpointFactory(ActionEndpointFactoryABC):
    """
    Handles case where `self` is unannotated - wraps the action function adding an annotation
    """

    priority: int = 250
    skip: bool = False

    def create(
        self,
        action: Action,
        skip_args: Set[str],
        factories: List[ActionEndpointFactoryABC],
    ) -> Optional[ActionEndpointABC]:
        if self.skip:
            return
        sig = inspect.signature(action.fn)
        params = list(sig.parameters.values())
        if (
            not params
            or params[0].name != "self"
            or params[0].annotation != inspect.Signature.empty
        ):
            return

        # noinspection PyUnresolvedReferences
        subject_module = importlib.import_module(action.fn.__module__)
        subject_class_name = action.fn.__qualname__.split(".")[0]
        subject_class = getattr(subject_module, subject_class_name)

        def wrapper(*args, **kwargs):
            result = action.fn(*args, **kwargs)
            return result

        params[0] = params[0].replace(annotation=subject_class)
        wrapper.__signature__ = sig.replace(parameters=params)
        wrapped_action = dataclasses.replace(action, fn=wrapper)
        action_endpoint = self._get_wrapped_endpoint(
            wrapped_action, skip_args, factories
        )
        return action_endpoint

    def _get_wrapped_endpoint(
        self,
        action: Action,
        skip_args: Set[str],
        factories: List[ActionEndpointFactoryABC],
    ) -> Optional[ActionEndpointABC]:
        self.skip = True
        try:
            for factory in factories:
                action_endpoint = factory.create(action, skip_args, factories)
                if action_endpoint:
                    return action_endpoint
        finally:
            self.skip = False
