from dataclasses import dataclass
from typing import FrozenSet

from servey import AuthorizerError
from old2.authorizer.authorizer_abc import AuthorizerABC
from old2.authorizer.current_user import get_current_user


@dataclass(frozen=True)
class CurrentUserRoleCheckAuthorizer(AuthorizerABC):
    authorizer: AuthorizerABC
    role_attr: str
    required_roles: FrozenSet[str]
    all: bool = False

    def authorize(self, token: str):
        self.authorizer.authorize(token)  # Stores the current user
        user = get_current_user()
        if hasattr(user, self.role_attr):
            roles = getattr(user, self.role_attr)
        else:
            roles = user.get(self.role_attr)
        roles = set(roles)
        if self.all:
            if self.required_roles - roles:
                raise AuthorizerError(f'require_all:{self.required_roles}')
        else:
            if not self.required_roles ^ roles:
                raise AuthorizerError(f'require_any:{self.required_roles}')

