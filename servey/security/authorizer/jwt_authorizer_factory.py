import base64
import os
from logging import getLogger

from servey.security.authorizer.authorizer_abc import AuthorizerABC
from servey.security.authorizer.authorizer_factory_abc import AuthorizerFactoryABC

LOGGER = getLogger(__name__)


class JwtAuthorizerFactory(AuthorizerFactoryABC):
    """
    Factory for authorizers that try to generate / validate jwt tokens using a private key
    defined specified as an environment variable: JWT_SECRET_KEY
    """

    priority = 50

    def create_authorizer(self) -> AuthorizerABC:
        try:
            from servey.security.authorizer.jwt_authorizer import JwtAuthorizer

            jwt_secret_key = os.environ.get("JWT_SECRET_KEY")
            if jwt_secret_key is None:
                LOGGER.warning(
                    "JWT_SECRET_KEY NOT DEFINED - Making One Up! (Auth will fail between restarts!)"
                )
                jwt_secret_key = base64.b64encode(os.urandom(12)).decode("UTF-8")
            authorizer = JwtAuthorizer(jwt_secret_key)
            return authorizer
        except ModuleNotFoundError:
            LOGGER.info("PyJWT is not available - skipping JwtAuthorizer")
