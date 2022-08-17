from dataclasses import field, dataclass
from inspect import Parameter, Signature
from typing import Tuple, Dict, Any

from fastapi import Depends, FastAPI

from servey.access_control.action_access_control_abc import ActionAccessControlABC
from servey.access_control.allow_all import ALLOW_ALL
from servey.access_control.authorization import Authorization, AuthorizationError
from servey.access_control.authorizer_abc import AuthorizerABC
from servey.access_control.authorizer_factory_abc import get_default_authorizer
from servey.access_control.filter import is_authorization, get_authorization_field_name
from servey.action import Action
from servey.executor import Executor
from servey.integration.fastapi_integration.authenticator.factory.authenticator_factory_abc import (
    get_default_authenticator,
)
from servey.integration.fastapi_integration.handler_filter.handler_filter_abc import (
    HandlerFilterABC,
    ExecutorFn,
)
from servey.integration.fastapi_integration.authenticator.authenticator_abc import (
    AuthenticatorABC,
)
from servey.trigger.web_trigger import WebTrigger


@dataclass
class AuthorizationHandlerFilter(HandlerFilterABC):
    priority: int = 80
    authorizer: AuthorizerABC = field(default_factory=get_default_authorizer)
    authenticator: AuthenticatorABC = field(default_factory=get_default_authenticator)
    # What to name the authorization parameter if none exists.
    authorization_kwarg_name: str = "servey_authorization"
    has_authenticated_actions: bool = False

    def filter(
        self, action: Action, trigger: WebTrigger, fn: ExecutorFn, sig: Signature
    ) -> Tuple[ExecutorFn, Signature, bool]:
        authorization_field_name = get_authorization_field_name(action)

        parameters = []
        authorization_kwarg_name = None
        for param in sig.parameters.values():
            if is_authorization(param.annotation):
                param = param.replace(default=self.create_get_authorization_default())
                authorization_kwarg_name = param.name
            parameters.append(param)

        filter_authorization_kwarg = False
        if not authorization_kwarg_name:
            if (
                not authorization_field_name
                and action.action_meta.access_control == ALLOW_ALL
            ):
                # No authorization going on here...
                return fn, sig, True
            authorization_kwarg_name = self.authorization_kwarg_name
            filter_authorization_kwarg = True
            parameters.append(
                Parameter(
                    name=authorization_kwarg_name,
                    kind=Parameter.KEYWORD_ONLY,
                    default=self.create_get_authorization_default(),
                )
            )

        fn = _wrap_fn(
            action.action_meta.access_control,
            authorization_field_name,
            authorization_kwarg_name,
            filter_authorization_kwarg,
            fn,
        )
        sig = sig.replace(parameters=parameters)
        self.has_authenticated_actions = True
        return fn, sig, True

    def create_get_authorization_default(self):
        async def get_authorization(
            token: str = Depends(self.authenticator.get_schema()),
        ):
            return self.authorizer.authorize(token)

        return Depends(get_authorization)

    def mount_dependencies(self, api: FastAPI):
        if self.has_authenticated_actions:
            self.authenticator.mount_authenticator(api, self.authorizer)


def _wrap_fn(
    access_control: ActionAccessControlABC,
    authorization_field_name: str,
    authorization_kwarg_name: str,
    filter_authorization_kwarg: bool,
    fn: ExecutorFn,
) -> ExecutorFn:
    def executor(ex: Executor, params: Dict[str, Any]) -> Any:
        authorization: Authorization = params[authorization_kwarg_name]
        if not access_control.is_executable(authorization):
            raise AuthorizationError()
        if authorization_field_name:
            setattr(ex.subject, authorization_field_name, authorization)
        if filter_authorization_kwarg:
            params.pop(authorization_kwarg_name, None)
        return fn(ex, params)

    return executor
