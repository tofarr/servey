from abc import abstractmethod, ABC
from typing import Optional

from marshy.factory.impl_marshaller_factory import get_impls

from servey.integration.fastapi_integration.authenticator.authenticator_abc import (
    AuthenticatorABC,
)


class AuthenticatorFactoryABC(ABC):
    priority: int = 100

    @abstractmethod
    def create_authenticator(self) -> Optional[AuthenticatorABC]:
        """Create a new authorizer instance. Return None if this was not possible"""


def create_authenticator():
    """
    Use the highest priority factory that can actually do it to create an authenticator.
    """
    factories = list(get_impls(AuthenticatorFactoryABC))
    factories.sort(key=lambda f: f.priority, reverse=True)
    for factory in factories:
        authorizer = factory().create_authenticator()
        if authorizer:
            return authorizer


_default_authenticator = None


def get_default_authenticator():
    global _default_authenticator
    if not _default_authenticator:
        _default_authenticator = create_authenticator()
    return _default_authenticator
