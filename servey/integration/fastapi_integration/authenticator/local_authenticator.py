from dataclasses import dataclass
from logging import getLogger
from typing import Any

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from servey.access_control.authorization import Authorization
from servey.access_control.authorizer_abc import AuthorizerABC

from servey.integration.fastapi_integration.authenticator.authenticator_abc import AuthenticatorABC

LOGGER = getLogger(__name__)


@dataclass
class LocalAuthenticator(AuthenticatorABC):
    """
    Most authentication is going to require some sort of access to a persistence mechanism,
    which is out of scope for servey. This implementation supplies authentication based on
    a preset username / password combo
    """
    username: str
    password: str
    authorization: Authorization
    path: str = '/login'
    priority: int = 50  # Lower than standard priority - anything should override this

    def mount_authenticator(self, fastapi: FastAPI, authorizer: AuthorizerABC):
        @fastapi.post(self.path)
        async def login(form_data: OAuth2PasswordRequestForm = Depends()):
            if form_data.username == self.username and form_data.password == self.password:
                return {
                    "access_token": authorizer.encode(self.authorization),
                    "token_type": "bearer"
                }
            raise HTTPException(status_code=400, detail="Incorrect username or password")

    def get_schema(self) -> Any:
        return OAuth2PasswordBearer(tokenUrl=self.path)
