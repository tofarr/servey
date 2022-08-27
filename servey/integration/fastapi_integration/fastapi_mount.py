from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any

from fastapi import FastAPI

from servey.action import Action
from servey.action_context import ActionContext, get_default_action_context
from servey.executor import Executor
from servey.integration.fastapi_integration.handler_filter.fastapi_handler_filter_abc import (
    FastapiHandlerFilterABC,
)
from servey.trigger.web_trigger import WebTrigger


@dataclass
class FastapiMount:
    """Utility for mounting actions to fastapi_integration."""

    api: FastAPI
    handler_filters: Tuple[FastapiHandlerFilterABC, ...]
    path_pattern: str = "/actions/{action_name}"

    def mount_all(self, action_context: Optional[ActionContext] = None):
        if not action_context:
            action_context = get_default_action_context()
        for action, trigger in action_context.get_actions_with_trigger_type(WebTrigger):
            self.mount_action(action, trigger)
        for handler_filter in self.handler_filters:
            handler_filter.mount_dependencies(self.api)

    def mount_action(self, action: Action, trigger: WebTrigger):
        """
        Mount an action to fast api, filtering it using available filters to provide integration.
        """
        path = self.path_pattern.format(action_name=action.action_meta.name)
        method = getattr(
            self.api, trigger.method.value
        )  # method may be get, put, post, patch, delete
        route_wrapper = method(path)
        handler = self.create_handler_for_action(action, trigger)
        route_wrapper(handler)

    def create_handler_for_action(self, action: Action, trigger: WebTrigger):
        fn = _handler
        sig = action.get_signature()
        for handler_filter in self.handler_filters:
            fn, sig, continue_filtering = handler_filter.filter(
                action, trigger, fn, sig
            )
            if not continue_filtering:
                break

        def route_handler(**kwargs):
            executor = action.create_executor()
            result = fn(executor, kwargs)
            return result

        route_handler.__signature__ = sig
        return route_handler


def _handler(executor: Executor, params: Dict[str, Any]) -> Any:
    return executor.execute(**params)
