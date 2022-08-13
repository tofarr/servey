from dataclasses import dataclass
from inspect import signature
from typing import Optional, Callable

from fastapi import FastAPI, Depends
from marshy.factory.optional_marshaller_factory import get_optional_type

from servey.access_control.authorization import Authorization
from servey.access_control.authorizer_abc import AuthorizerABC
from servey.action import Action
from servey.action_context import ActionContext, get_default_action_context
from servey.integration.fastapi_integration.authenticator.authenticator_abc import AuthenticatorABC
from servey.trigger.web_trigger import WebTrigger


@dataclass
class FastapiMount:
    """ Utility for mounting actions to fastapi_integration. """
    api: FastAPI
    authorizer: AuthorizerABC
    authenticator: AuthenticatorABC
    path_pattern: str = '/actions/{action_name}'

    def mount_all(self, action_context: Optional[ActionContext] = None):
        if not action_context:
            action_context = get_default_action_context()
        for action, trigger in action_context.get_actions_with_trigger_type(WebTrigger):
            self.mount_action(action, trigger)
        if self.authenticator:
            self.authenticator.mount_authenticator(self.api, self.authorizer)

    def mount_action(self, action: Action, trigger: WebTrigger):
        web_trigger = _get_web_trigger(action)
        if not web_trigger:
            return
        path = self.path_pattern.format(action_name=action.action_meta.name)
        method = getattr(self.api, web_trigger.method.value)  # method may be get, put, post, patch, delete
        wrapper = method(path)
        wrapper(self.with_modified_signature_for_authorization(action))

    def with_modified_signature_for_authorization(self, action: Action) -> Callable:
        def fn(**kwargs):
            return action.fn(**kwargs)

        schema = self.authenticator.get_schema()
        authorizer = self.authorizer

        async def get_authorization(token: str = Depends(schema)) -> Authorization:
            return authorizer.authorize(token)

        sig = signature(action.fn)
        params = []
        for param in sig.parameters.values():
            if param.name == 'authorization':
                type_ = param.annotation
                type_ = get_optional_type(type_) or type_
                if type_ == Authorization:
                    param = param.replace(default=Depends(get_authorization))
            params.append(param)
        sig = sig.replace(parameters=tuple(params))
        fn.__signature__ = sig
        return fn


def _get_web_trigger(action: Action) -> Optional[WebTrigger]:
    trigger = next((t for t in action.action_meta.triggers if isinstance(t, WebTrigger)), None)
    return trigger
