from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer

from servey.access_control.authorizer_abc import AuthorizerABC
from servey.integration.fastapi_integration.authenticator.authenticator_abc import AuthenticatorABC


@dataclass
class RemoteAuthenticator(AuthenticatorABC):
    """ OAuth2 authenticator which is in a different domain """
    url: str

    def mount_authenticator(self, fastapi: FastAPI, authorizer: AuthorizerABC):
        # The authenticator is not local - nothing to mount!
        pass

    def get_schema(self) -> Any:
        return OAuth2PasswordBearer(tokenUrl=self.url)
