import base64
import json
from base64 import urlsafe_b64encode
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, Dict

import boto3
import jwt
from jwt import DecodeError
from schemey.util import filter_none

from servey.security.authorization import Authorization, AuthorizationError
from servey.security.authorizer.authorizer_abc import AuthorizerABC
from servey.security.authorizer.jwt_authorizer import date_from_jwt


@dataclass
class KmsAuthorizer(AuthorizerABC):
    """
    Authorizer that uses kms to work with tokens, offloading the responsibility for key
    management to AWS. I would have loved to use cognito for this, but was hampered
    by it not having the ability to specify custom per user scopes in the access token.

    Encoding a JWT token requires use of the private key, and always goes out to kms.
    Verification only uses the public key, which is cached locally.

    Note: When decoding, this implementation only grabs what is available in KMS
    it makes no distinction about filtering to a particular subset of keys. That sort
    of logic would probably require a class with an attached persistence mechanism
    """

    key_id: str
    iss: Optional[str] = None
    aud: Optional[str] = None
    kms: Optional[Any] = None
    public_keys: Optional[Dict[str, str]] = field(default_factory=dict)

    def __post_init__(self):
        if not self.kms:
            self.kms = boto3.client("kms")

    def encode(self, authorization: Authorization) -> str:
        header = urlsafe_b64encode(
            json.dumps(dict(typ="JWT", alg="RS256", kid=self.key_id)).encode()
        )
        payload = urlsafe_b64encode(
            json.dumps(
                filter_none(
                    dict(
                        iss=self.iss,
                        sub=authorization.subject_id,
                        aud=self.aud,
                        exp=int(authorization.expire_at.timestamp())
                        if authorization.expire_at
                        else None,
                        nbf=int(authorization.not_before.timestamp())
                        if authorization.not_before
                        else None,
                        iat=int(datetime.now().timestamp()),
                        scope=" ".join(authorization.scopes),
                    )
                )
            ).encode()
        )
        message = header + b"." + payload
        # noinspection SpellCheckingInspection
        result = self.kms.sign(
            Message=message,
            KeyId=self.key_id,
            SigningAlgorithm="RSASSA_PKCS1_V1_5_SHA_256",
            MessageType="RAW",
        )
        signature = urlsafe_b64encode(result["Signature"])
        result = message + b"." + signature
        return result.decode("UTF-8")

    @staticmethod
    def get_key_id(token: str) -> str:
        """May need the key id from the token header in order to figure out which key to use"""
        headers = jwt.get_unverified_header(token)
        return headers["kid"]

    def get_public_key(self, key_id: str):
        public_key = self.public_keys.get(key_id)
        if not public_key:
            response = self.kms.get_public_key(KeyId=key_id)
            public_key = response["PublicKey"]
            public_key = base64.b64encode(public_key).decode()
            public_key = (
                "-----BEGIN PUBLIC KEY-----\n"
                + public_key
                + "\n-----END PUBLIC KEY-----"
            ).encode()
            # noinspection PyTypeChecker
            self.public_keys[public_key] = public_key

        return public_key

    def authorize(self, token: str) -> Authorization:
        """
        Verifying tokens only requires the public key. We cache this from kms to do verifications
        locally which is more efficient
        """
        try:
            header = jwt.get_unverified_header(token)
            key_id = header.get("kid")
            public_key = self.get_public_key(key_id)
            decoded = jwt.decode(jwt=token, key=public_key, algorithms=["RS256"])
            authorization = Authorization(
                subject_id=decoded.get("sub"),
                not_before=date_from_jwt(decoded, "nbf"),
                expire_at=date_from_jwt(decoded, "exp"),
                scopes=frozenset(decoded.get("scope").split(" ")),
            )
            return authorization
        except DecodeError as e:
            raise AuthorizationError(e)
