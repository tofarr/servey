from abc import ABC, abstractmethod
from typing import Optional

from marshy.factory.impl_marshaller_factory import get_impls

from servey.security.authorization import Authorization


class PasswordAuthenticatorABC(ABC):
    priority: int = 100

    @abstractmethod
    def authenticate(self, username: str, password: str) -> Optional[Authorization]:
        """Authenticate the username and password given"""


def get_default_password_authenticator() -> PasswordAuthenticatorABC:
    impls = list(get_impls(PasswordAuthenticatorABC))
    impls.sort(key=lambda i: i.priority, reverse=True)
    return impls[0]()
