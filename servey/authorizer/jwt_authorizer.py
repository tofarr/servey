import dataclasses
from typing import Callable, Iterable, Optional

import jwt
from marshy.marshaller.marshaller_abc import MarshallerABC

from old2.authorizer.authorizer_abc import AuthorizerABC
from old2.authorizer.current_user import set_current_user


@dataclasses
class JwtAuthorizer(AuthorizerABC):
    key_factory: Callable[[], str]  # Typically this yields a public key
    algorithms: Iterable[str] = ('RS256',)
    marshaller: Optional[MarshallerABC] = None

    def authorize(self, token: str):
        key = self.key_factory()
        user = jwt.decode(token, key, algorithms=self.algorithms)
        if self.marshaller:
            user = self.marshaller.load(user)
        set_current_user(user)