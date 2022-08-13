import os
from typing import Optional

from servey.integration.fastapi_integration.authenticator.authenticator_abc import AuthenticatorABC
from servey.integration.fastapi_integration.authenticator.factory.authenticator_factory_abc import AuthenticatorFactoryABC


class RemoteAuthenticatorFactory(AuthenticatorFactoryABC):
    priority: int = 80

    def create_authenticator(self) -> Optional[AuthenticatorABC]:
        from servey.integration.fastapi_integration.authenticator.remote_authenticator import RemoteAuthenticator
        url = os.environ.get('SERVEY_AUTHENTICATION_URL')
        if url:
            return RemoteAuthenticator(url)
