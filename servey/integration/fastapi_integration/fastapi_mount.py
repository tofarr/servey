from dataclasses import dataclass
from typing import Optional, Callable, Tuple

from fastapi import FastAPI

from servey.access_control.authorizer_abc import AuthorizerABC
from servey.action import Action
from servey.action_context import ActionContext, get_default_action_context
from servey.integration.fastapi_integration.authenticator.authenticator_abc import (
    AuthenticatorABC,
)
from servey.integration.fastapi_integration.executor_factory.fastapi_handler_factory_abc import (
    FastapiHandlerFactoryABC,
)
from servey.trigger.web_trigger import WebTrigger


@dataclass
class FastapiMount:
    """Utility for mounting actions to fastapi_integration."""

    api: FastAPI
    handler_factories: Tuple[FastapiHandlerFactoryABC, ...]
    path_pattern: str = "/actions/{action_name}"

    def mount_all(self, action_context: Optional[ActionContext] = None):
        if not action_context:
            action_context = get_default_action_context()
        for action, trigger in action_context.get_actions_with_trigger_type(WebTrigger):
            self.mount_action(action, trigger)
        for handler_factory in self.handler_factories:
            handler_factory.mount_dependencies(self.api)

    def mount_action(self, action: Action, trigger: WebTrigger):
        path = self.path_pattern.format(action_name=action.action_meta.name)
        method = getattr(
            self.api, trigger.method.value
        )  # method may be get, put, post, patch, delete
        wrapper = method(path)
        handler = self.create_handler_for_action(action, trigger)
        wrapper(handler)

    def create_handler_for_action(self, action: Action, trigger: WebTrigger):
        for handler_factory in self.handler_factories:
            handler = handler_factory.create_handler_for_action(action, trigger)
            if handler:
                return handler


def _get_web_trigger(action: Action) -> Optional[WebTrigger]:
    trigger = next(
        (t for t in action.action_meta.triggers if isinstance(t, WebTrigger)), None
    )
    return trigger
