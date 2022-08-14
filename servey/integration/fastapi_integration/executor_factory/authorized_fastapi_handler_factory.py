from dataclasses import dataclass, field, fields
from inspect import Parameter, Signature
from typing import Callable, Optional, Tuple

from fastapi import Depends, FastAPI
from marshy.factory.optional_marshaller_factory import get_optional_type

from servey.access_control.allow_all import ALLOW_ALL
from servey.access_control.authorization import Authorization
from servey.access_control.authorizer_abc import AuthorizerABC
from servey.access_control.authorizer_factory_abc import create_authorizer
from servey.action import Action
from servey.integration.fastapi_integration.authenticator.authenticator_abc import (
    AuthenticatorABC,
)
from servey.integration.fastapi_integration.authenticator.factory.authenticator_factory_abc import (
    create_authenticator,
)
from servey.integration.fastapi_integration.executor_factory.fastapi_handler_factory_abc import (
    FastapiHandlerFactoryABC,
)
from servey.trigger.web_trigger import WebTrigger


@dataclass
class AuthorizedFastapiHandlerFactory(FastapiHandlerFactoryABC):
    """
    Invokable factory that adds support for authorization.
    """

    priority: int = 80
    authorizer: AuthorizerABC = field(default_factory=create_authorizer)
    authenticator: AuthenticatorABC = field(default_factory=create_authenticator)
    has_secured_actions: bool = False

    def __post_init__(self):
        async def get_authorization(
            token: str = Depends(self.authenticator.get_schema()),
        ):
            return self.authorizer.authorize(token)

        object.__setattr__(self, "get_authorization", get_authorization)

    def create_handler_for_action(
        self, action: Action, trigger: WebTrigger
    ) -> Optional[Callable]:
        # If there is no authorizer, there is no way to authenticate anything!
        if not self.authorizer or not self.authenticator:
            return

        sig, authorization_param_name, is_kwarg = self.create_signature(action)
        authorization_field_name = self.get_authorization_field_name(action)

        if (
            not is_kwarg
            and not authorization_field_name
            and action.action_meta.access_control is ALLOW_ALL
        ):
            return  # This action is not secured

        def handle(**kwargs):
            authorization = kwargs.get(authorization_param_name)
            if not is_kwarg:
                # The subject function does not take an authorization parameter, so we remove it
                kwargs.pop(authorization_param_name, None)
            executor = action.create_executor()
            if authorization_field_name:
                # Authorization param is injected as a field
                injection_subject = executor.get_injection_subject()
                setattr(injection_subject, authorization_field_name, authorization)
            result = executor.execute(**kwargs)
            return result

        self.has_secured_actions = True

        handle.__name__ = action.action_meta.name
        handle.__signature__ = sig
        return handle

    def create_signature(self, action: Action) -> Tuple[Signature, str, bool]:
        param_name = None
        is_kwarg = False
        sig = action.get_signature()
        parameters = []
        for param in sig.parameters.values():
            type_ = param.annotation
            if (get_optional_type(type_) or type_) == Authorization:
                param_name = param.name
                is_kwarg = True
                param = param.replace(default=Depends(self.get_authorization))
            parameters.append(param)
        if not param_name:
            param_name = "authorization"
            parameters.append(
                Parameter(
                    param_name,
                    Parameter.KEYWORD_ONLY,
                    default=Depends(self.get_authorization),
                    annotation=Optional[Authorization],
                )
            )
        sig = sig.replace(parameters=tuple(parameters))
        return sig, param_name, is_kwarg

    @staticmethod
    def get_authorization_field_name(action: Action) -> Optional[str]:
        if action.method_name:
            for field in fields(action.subject):
                type_ = field.type
                if (get_optional_type(type_) or type_) == Authorization:
                    return field.name

    def mount_dependencies(self, api: FastAPI):
        if self.has_secured_actions:
            self.authenticator.mount_authenticator(api, self.authorizer)
