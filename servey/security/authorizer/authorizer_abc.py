from abc import abstractmethod, ABC

from servey.security.authorization import Authorization


class AuthorizerABC(ABC):
    @abstractmethod
    def authorize(self, token: str) -> Authorization:
        """Convert the token given to an authorization object"""

    @abstractmethod
    def encode(self, authorization: Authorization) -> str:
        """Encode the authorization given as a string which may be included in an authorization header"""
