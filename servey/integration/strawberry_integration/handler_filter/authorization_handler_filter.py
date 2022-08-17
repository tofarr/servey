from dataclasses import dataclass, field
from inspect import Signature, Parameter
from typing import Any, Dict, Optional, Tuple

from strawberry.types import Info

from servey.access_control.action_access_control_abc import ActionAccessControlABC
from servey.access_control.allow_all import ALLOW_ALL
from servey.access_control.authorization import Authorization, AuthorizationError
from servey.access_control.authorizer_abc import AuthorizerABC
from servey.access_control.authorizer_factory_abc import get_default_authorizer
from servey.access_control.filter import get_authorization_field_name, is_authorization
from servey.action import Action
from servey.executor import Executor
from servey.integration.strawberry_integration.handler_filter.handler_filter_abc import (
    HandlerFilterABC,
    ExecutorFn,
)
from servey.integration.strawberry_integration.schema_factory import SchemaFactory
from servey.trigger.web_trigger import WebTrigger


@dataclass
class AuthorizationHandlerFilter(HandlerFilterABC):
    priority: int = 120
    authorizer: AuthorizerABC = field(default_factory=get_default_authorizer)
    # What to name the authorization parameter if none exists.
    info_kwarg_name: str = "strawberry_info"

    def filter(
        self,
        action: Action,
        trigger: WebTrigger,
        fn: ExecutorFn,
        sig: Signature,
        schema_factory: SchemaFactory,
    ) -> Tuple[ExecutorFn, Signature, bool]:
        authorization_field_name = get_authorization_field_name(action)

        parameters = []
        authorization_kwarg_name = None
        for param in sig.parameters.values():
            if is_authorization(param.annotation):
                authorization_kwarg_name = param.name
            else:
                parameters.append(param)

        if not authorization_kwarg_name:
            if (
                not authorization_field_name
                and action.action_meta.access_control == ALLOW_ALL
            ):
                # No authorization going on here...
                return fn, sig, True

        parameters.append(
            Parameter(
                name=self.info_kwarg_name, kind=Parameter.KEYWORD_ONLY, annotation=Info
            )
        )

        fn = self._wrap_fn(
            action.action_meta.access_control,
            authorization_field_name,
            authorization_kwarg_name,
            fn,
        )
        sig = sig.replace(parameters=parameters)
        return fn, sig, True

    def _wrap_fn(
        self,
        access_control: ActionAccessControlABC,
        authorization_field_name: Optional[str],
        authorization_kwarg_name: Optional[str],
        fn: ExecutorFn,
    ) -> ExecutorFn:
        def executor(ex: Executor, params: Dict[str, Any]) -> Any:
            info = params[self.info_kwarg_name]
            authorization = self.get_authorization(info)
            params.pop(self.info_kwarg_name, None)
            if not access_control.is_executable(authorization):
                raise AuthorizationError()
            if authorization_field_name:
                setattr(ex.subject, authorization_field_name, authorization)
            if authorization_kwarg_name:
                params[authorization_kwarg_name] = authorization
            return fn(ex, params)

        return executor

    def get_authorization(self, info: Info) -> Optional[Authorization]:
        authorization = info.context.get("authorization")
        if authorization:
            return authorization
        request = info.context.get("request")
        if request:
            token = request.headers.get("Authorization")
            if token and token.startswith("Bearer "):
                token = token[7:]
                authorization = self.authorizer.authorize(token)
                info.context["authorization"] = authorization
                return authorization
