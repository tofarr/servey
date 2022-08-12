from abc import abstractmethod, ABC

from servey.access_control.authorization import Authorization


class AuthorizerABC(ABC):

    @abstractmethod
    def authorize(self, token: str) -> Authorization:
        """ Convert the jwt token given to an authorization object """
