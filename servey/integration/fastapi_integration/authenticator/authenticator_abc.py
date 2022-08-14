from abc import abstractmethod, ABC
from typing import Any

from fastapi import FastAPI

from servey.access_control.authorizer_abc import AuthorizerABC


class AuthenticatorABC(ABC):
    @abstractmethod
    def mount_authenticator(self, fastapi: FastAPI, authorizer: AuthorizerABC):
        """Mount authentication to the fast api given"""

    @abstractmethod
    def get_schema(self) -> Any:
        """Get the authorization schema for this Authenticator. (Typically OAuth2PasswordBearer)"""
