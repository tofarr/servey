import os
from datetime import datetime
from unittest import TestCase
from unittest.mock import patch, MagicMock

from servey.security.authorization import ROOT, Authorization, AuthorizationError
from servey.servey_aws.authorizer.kms_authorizer_factory import KmsAuthorizerFactory


class TestKmsAuthorizer(TestCase):
    def test_authorizer(self):
        mock_client = MagicMock()
        mock_client.return_value.sign.return_value = {"Signature": b"NotARealSignature"}
        mock_client.return_value.get_public_key.return_value = {
            "PublicKey": b"NotARealPublicKey"
        }
        nbf = int(datetime.now().timestamp())
        exp = nbf + 3600
        with (
            patch.dict(os.environ, {"KMS_KEY_ID": "some_key"}),
            patch("boto3.client", mock_client),
            patch(
                "jwt.decode",
                return_value={
                    "sub": "some-sub",
                    "nbf": nbf,
                    "exp": exp,
                    "scope": "foo bar",
                },
            ),
        ):
            factory = KmsAuthorizerFactory()
            authorizer = factory.create_authorizer()
            token = authorizer.encode(ROOT)
            # noinspection PyUnresolvedReferences
            self.assertEqual("alias/some_key", authorizer.get_key_id(token))
            auth = authorizer.authorize(token)
            self.assertEqual(
                Authorization(
                    subject_id="some-sub",
                    not_before=datetime.fromtimestamp(nbf),
                    expire_at=datetime.fromtimestamp(exp),
                    scopes=frozenset(("foo", "bar")),
                ),
                auth,
            )

    def test_authorize_invalid(self):
        mock_client = MagicMock()
        with (
            patch.dict(os.environ, {"KMS_KEY_ID": "some_key"}),
            patch("boto3.client", mock_client),
        ):
            factory = KmsAuthorizerFactory()
            authorizer = factory.create_authorizer()
            with self.assertRaises(AuthorizationError):
                authorizer.authorize("notAValidToken")
