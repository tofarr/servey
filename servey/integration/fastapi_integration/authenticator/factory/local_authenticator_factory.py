import base64
import os
from logging import getLogger

from servey.access_control.authorization import ROOT
from servey.integration.fastapi_integration.authenticator.authenticator_abc import (
    AuthenticatorABC,
)
from servey.integration.fastapi_integration.authenticator.factory.authenticator_factory_abc import (
    AuthenticatorFactoryABC,
)

LOGGER = getLogger(__name__)


class LocalAuthenticatorFactory(AuthenticatorFactoryABC):
    priority: int = 80

    def create_authenticator(self) -> AuthenticatorABC:
        from servey.integration.fastapi_integration.authenticator.local_authenticator import (
            LocalAuthenticator,
        )

        username = os.environ.get("SERVEY_AUTHENTICATOR_USERNAME") or "root"
        password = os.environ.get("SERVEY_AUTHENTICATOR_PASSWORD")
        path = os.environ.get("SERVEY_AUTHENTICATOR_PATH") or LocalAuthenticator.path
        if password is None:
            password = (
                base64.b64encode(os.urandom(12))
                .decode("UTF-8")
                .replace("+", "")
                .replace("/", "")
            )
            LOGGER.warning(f"Using Temporary Password: {password}")
        return LocalAuthenticator(username, password, ROOT, path)
