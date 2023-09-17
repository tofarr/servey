from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

import jwt
from jwt import InvalidTokenError
from schemey.util import filter_none

from servey.security.authorization import Authorization, AuthorizationError
from servey.security.authorizer.jwt_authorizer_abc import JwtAuthorizerABC


@dataclass
class JwtAuthorizer(JwtAuthorizerABC):
    """
    Encoder that uses pyjwt and a locally stored key to work with tokens. In the AWS environment,
    it is probably better to use kms or cognito for this (Though cognito is hampered by not having
    the ability to specify custom per user scopes in the access token)
    """

    private_key: Any
    algorithm: str = "HS256"
    kid: Optional[str] = None
    iss: Optional[str] = None
    aud: Optional[str] = None

    def encode(self, authorization: Authorization) -> str:
        headers = filter_none({"kid": self.kid})
        encoded = jwt.encode(
            headers=headers,
            payload=filter_none(
                {
                    "iss": self.iss,
                    "sub": authorization.subject_id,
                    "aud": self.aud,
                    "exp": int(authorization.expire_at.timestamp())
                    if authorization.expire_at
                    else None,
                    "nbf": int(authorization.not_before.timestamp())
                    if authorization.not_before
                    else None,
                    "iat": int(datetime.now().timestamp()),
                    "scope": " ".join(authorization.scopes),
                }
            ),
            key=self.private_key,
            algorithm=self.algorithm,
        )
        return encoded

    @staticmethod
    def get_key_id(token: str) -> str:
        """May need the key id from the token header in order to figure out which key to use"""
        headers = jwt.get_unverified_header(token)
        return headers["kid"]

    def authorize(self, token: str) -> Authorization:
        try:
            decoded = jwt.decode(
                jwt=token,
                key=self.private_key,
                algorithms=["HS256", "RS256"],
                audience=self.aud,
                issuer=self.iss,
            )
            authorization = self.authorization_from_decoded(decoded)
            return authorization
        except InvalidTokenError as e:
            raise AuthorizationError(e) from e
