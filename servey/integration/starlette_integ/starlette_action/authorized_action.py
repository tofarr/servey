from dataclasses import dataclass
from typing import Tuple, Dict, Any, Optional

from starlette.exceptions import HTTPException
from starlette.requests import Request

from servey.access_control.authorization import Authorization, AuthorizationError
from servey.access_control.authorizer_abc import AuthorizerABC
from servey.executor import Executor
from servey.integration.starlette_integ.starlette_action.action_route_wrapper_abc import (
    ActionRouteWrapperABC,
)


@dataclass
class AuthorizedAction(ActionRouteWrapperABC):
    authorizer: AuthorizerABC
    kwarg_name: Optional[str]
    field_name: Optional[str]

    async def parse(self, request: Request) -> Tuple[Executor, Dict[str, Any]]:
        authorization = self.get_authorization(request)
        access_control = self.get_action().action_meta.access_control
        if not access_control.is_executable(authorization):
            raise HTTPException(401)
        executor, kwargs = super().parse(request)
        if self.kwarg_name:
            kwargs[self.kwarg_name] = authorization
        if self.field_name:
            setattr(executor, self.field_name, authorization)
        return executor, kwargs

    def get_authorization(self, request: Request) -> Optional[Authorization]:
        try:
            token = request.headers.get("authorization")
            if not token:
                return
            authorization = self.authorizer.authorize(token)
            return authorization
        except AuthorizationError:
            raise HTTPException(403)
