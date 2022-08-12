import os
from logging import getLogger
from typing import Optional
from uuid import uuid4

from servey.access_control.authorizer_abc import AuthorizerABC
from servey.access_control.authorizer_factory_abc import AuthorizerFactoryABC

LOGGER = getLogger(__name__)


class KmsAuthorizerFactory(AuthorizerFactoryABC):
    """
    Factory for authorizers that requires that boto3 is available and that
    an appropriate key exists in the kms
    """
    priority = 80

    def create_authorizer(self) -> Optional[AuthorizerABC]:
        try:
            # First we need a key id - this is stored in the SSM
            kms_key_id = os.environ.get('KMS_KEY_ID')
            if kms_key_id is None:
                LOGGER.debug('KMS_SECRET_KEY NOT DEFINED - SKIPPING...')
                jwt_secret_key = str(uuid4())
            from servey.access_control.jwt_authorizer import JwtAuthorizer
            authorizer = JwtAuthorizer(jwt_secret_key)
            return authorizer
        except ModuleNotFoundError:
            LOGGER.info('PyJWT is not available - skipping JwtAuthorizer')
