from dataclasses import dataclass, field
from typing import List, Optional, Set

from servey.action.action import Action
from servey.security.access_control.allow_all import ALLOW_ALL
from servey.security.authorization import get_inject_at
from servey.security.authorizer.authorizer_abc import AuthorizerABC
from servey.security.authorizer.authorizer_factory_abc import get_default_authorizer
from servey.servey_starlette.action_endpoint.action_endpoint_abc import (
    ActionEndpointABC,
)
from servey.servey_starlette.action_endpoint.authorizing_action_endpoint import (
    AuthorizingActionEndpoint,
)
from servey.servey_starlette.action_endpoint.factory.action_endpoint_factory_abc import (
    ActionEndpointFactoryABC,
)


@dataclass
class AuthorizingActionEndpointFactory(ActionEndpointFactoryABC):
    priority: int = 200
    authorizer: AuthorizerABC = field(default_factory=get_default_authorizer)
    skip: bool = False

    def create(
        self,
        action: Action,
        skip_args: Set[str],
        factories: List[ActionEndpointFactoryABC],
    ) -> Optional[ActionEndpointABC]:
        if self.skip:
            return

        auth_kwarg_name = get_inject_at(action.fn)
        if not auth_kwarg_name and action.access_control == ALLOW_ALL:
            return
        if auth_kwarg_name:
            skip_args = skip_args.copy()
            skip_args.add(auth_kwarg_name)
        action_endpoint = self._get_wrapped_endpoint(action, skip_args, factories)
        if action_endpoint:
            return AuthorizingActionEndpoint(
                action_endpoint=action_endpoint,
                authorizer=self.authorizer,
                auth_kwarg_name=auth_kwarg_name,
            )

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
