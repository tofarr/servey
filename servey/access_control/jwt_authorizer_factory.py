import os
from logging import getLogger
from typing import Optional

from servey.access_control.authorizer_abc import AuthorizerABC
from servey.access_control.authorizer_factory_abc import AuthorizerFactoryABC

LOGGER = getLogger(__name__)


class JwtAuthorizerFactory(AuthorizerFactoryABC):
    """
    Factory for authorizers that try to generate / validate jwt tokens using a private key
    defined specified as an environment variable: JWT_SECRET_KEY
    """
    priority = 50

    def create_authorizer(self) -> Optional[AuthorizerABC]:
        try:
            jwt_secret_key = os.environ.get('JWT_SECRET_KEY')
            if jwt_secret_key is None:
                LOGGER.debug('JWT_SECRET_KEY NOT DEFINED - Skipping...')
                return None
            from servey.access_control.jwt_authorizer import JwtAuthorizer
            authorizer = JwtAuthorizer(jwt_secret_key)
            return authorizer
        except ModuleNotFoundError:
            LOGGER.info('PyJWT is not available - skipping JwtAuthorizer')
