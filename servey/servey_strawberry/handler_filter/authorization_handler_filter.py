import dataclasses
import inspect
from dataclasses import dataclass, field
from inspect import Parameter
from typing import Optional, Tuple

from marshy.factory.optional_marshaller_factory import get_optional_type
from strawberry.types import Info

from servey.action.action import Action
from servey.security.access_control.allow_all import ALLOW_ALL
from servey.security.authorization import Authorization, AuthorizationError
from servey.security.authorizer.authorizer_abc import AuthorizerABC
from servey.security.authorizer.authorizer_factory_abc import get_default_authorizer
from servey.servey_strawberry.handler_filter.handler_filter_abc import (
    HandlerFilterABC,
)
from servey.servey_strawberry.schema_factory import SchemaFactory


@dataclass
class AuthorizationHandlerFilter(HandlerFilterABC):
    priority: int = 120
    authorizer: AuthorizerABC = field(default_factory=get_default_authorizer)
    # What to name the authorization parameter if none exists.
    info_kwarg_name: str = "info"  # NOTE: It seems that strawberry reserves the name: Info for this parameter

    def filter(
        self,
        action: Action,
        schema_factory: SchemaFactory,
    ) -> Tuple[Action, bool]:
        fn = action.fn
        sig = inspect.signature(fn)

        parameters = []
        authorization_kwarg_name = None
        for param in sig.parameters.values():
            type_ = get_optional_type(param.annotation) or param.annotation
            if type_ is Authorization:
                authorization_kwarg_name = param.name
            else:
                parameters.append(param)

        if not authorization_kwarg_name and action.access_control == ALLOW_ALL:
            return action, True

        if authorization_kwarg_name:
            parameters.append(
                Parameter(
                    name=self.info_kwarg_name,
                    kind=Parameter.KEYWORD_ONLY,
                    annotation=Info,
                )
            )

        def resolver(*args, **kwargs):
            info = kwargs.pop(self.info_kwarg_name)
            authorization = self.get_authorization(info)
            if not action.access_control.is_executable(authorization):
                raise AuthorizationError()
            if authorization_kwarg_name:
                kwargs[authorization_kwarg_name] = authorization
            result = fn(*args, **kwargs)
            return result

        sig = sig.replace(parameters=parameters)
        resolver.__signature__ = sig
        wrapped_action = dataclasses.replace(action, fn=resolver)
        return wrapped_action, True

    def get_authorization(self, info: Info) -> Optional[Authorization]:
        authorization = info.context.get("authorization")
        if authorization:
            return authorization
        request = info.context.get("request")
        if request:
            token = request.headers.get("Authorization")
            if token and token.lower().startswith("bearer "):
                token = token[7:]
                authorization = self.authorizer.authorize(token)
                info.context["authorization"] = authorization
                return authorization
