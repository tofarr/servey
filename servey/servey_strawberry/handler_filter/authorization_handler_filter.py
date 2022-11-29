import inspect
from dataclasses import dataclass, field
from inspect import Parameter
from typing import Optional, Tuple, Callable

from strawberry.types import Info

from servey.action.action_meta import ActionMeta
from servey.action.trigger.web_trigger import WebTrigger
from servey.security.authorization import Authorization
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
    info_kwarg_name: str = "strawberry_info"

    def filter(
        self,
        fn: Callable,
        action_meta: ActionMeta,
        trigger: WebTrigger,
        schema_factory: SchemaFactory,
    ) -> Tuple[Callable, ActionMeta, bool]:
        sig = inspect.signature(fn)

        parameters = []
        authorization_kwarg_name = None
        for param in sig.parameters.values():
            if param.annotation is Authorization:
                authorization_kwarg_name = param.name
            else:
                parameters.append(param)

        if not authorization_kwarg_name:
            return fn, action_meta, True

        parameters.append(
            Parameter(
                name=self.info_kwarg_name, kind=Parameter.KEYWORD_ONLY, annotation=Info
            )
        )

        def resolver(**kwargs):
            info = kwargs.pop(self.info_kwarg_name)
            authorization = self.get_authorization(info)
            kwargs[authorization_kwarg_name] = authorization
            result = fn(**kwargs)
            return result

        sig = sig.replace(parameters=parameters)
        resolver.__signature__ = sig
        return resolver, action_meta, True

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
