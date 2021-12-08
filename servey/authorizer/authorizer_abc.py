from abc import ABC, abstractmethod


class AuthorizerABC(ABC):

    @abstractmethod
    def authorize(self, token: str):
        """ Authorize an operation. """
