import os
from logging import getLogger
from typing import Optional

from servey.security.authorizer.authorizer_abc import AuthorizerABC
from servey.security.authorizer.authorizer_factory_abc import AuthorizerFactoryABC

LOGGER = getLogger(__name__)


class KmsAuthorizerFactory(AuthorizerFactoryABC):
    """
    Factory for authorizers that requires that boto3 is available and that
    an appropriate key exists in the kms
    """

    priority = 80

    def create_authorizer(self) -> Optional[AuthorizerABC]:
        # First we need a key id - this is stored as an environment variable
        kms_key_id = os.environ.get("KMS_KEY_ID")
        if kms_key_id is None:
            LOGGER.debug("KMS_SECRET_KEY NOT DEFINED - SKIPPING...")
            return
        from servey.servey_aws.authorizer.kms_authorizer import KmsAuthorizer

        authorizer = KmsAuthorizer("alias/" + kms_key_id)
        return authorizer
