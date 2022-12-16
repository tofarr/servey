from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

import jwt
from jwt import InvalidTokenError
from marshy.types import ExternalItemType
from schemey.util import filter_none

from servey.security.authorization import Authorization, AuthorizationError
from servey.security.authorizer.authorizer_abc import AuthorizerABC


@dataclass
class JwtAuthorizer(AuthorizerABC):
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
        headers = filter_none(dict(kid=self.kid))
        encoded = jwt.encode(
            headers=headers,
            payload=filter_none(
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
            authorization = Authorization(
                subject_id=decoded.get("sub"),
                not_before=date_from_jwt(decoded, "nbf"),
                expire_at=date_from_jwt(decoded, "exp"),
                scopes=frozenset(decoded.get("scope").split(" ")),
            )
            return authorization
        except InvalidTokenError as e:
            raise AuthorizationError(e)


def date_from_jwt(decoded: ExternalItemType, key: str) -> Optional[datetime]:
    value = decoded.get(key)
    if value:
        return datetime.fromtimestamp(value)
