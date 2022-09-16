from abc import abstractmethod, ABC
from typing import Optional

from marshy.factory.impl_marshaller_factory import get_impls

from servey.security.authorizer.authorizer_abc import AuthorizerABC


class AuthorizerFactoryABC(ABC):
    priority: int = 100

    @abstractmethod
    def create_authorizer(self) -> Optional[AuthorizerABC]:
        """Create a new authorizer instance. Return None if this was not possible"""


def create_authorizer():
    """
    Use the highest priority factory that can actually do it to create an authorizer.
    For example, the KmsAuthorizerFactory requires that boto3 is available and that a KMS_KEY_ID specified
    as an environment variable, so will yield nothing if either of these constraints are not met.
    The JwtAuthorizationFactory has lower priority, will make up a key on the fly as required, but requires
    that pyjwt is installed.
    """
    factories = list(get_impls(AuthorizerFactoryABC))
    factories.sort(key=lambda f: f.priority, reverse=True)
    for factory in factories:
        authorizer = factory().create_authorizer()
        if authorizer:
            return authorizer


_default_authorizer = None


def get_default_authorizer():
    global _default_authorizer
    if not _default_authorizer:
        _default_authorizer = create_authorizer()
    return _default_authorizer
