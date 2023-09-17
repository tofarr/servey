from abc import ABC
from datetime import datetime
from typing import Optional

from marshy.types import ExternalItemType

from servey.security.authorization import Authorization
from servey.security.authorizer.authorizer_abc import AuthorizerABC


class JwtAuthorizerABC(AuthorizerABC, ABC):
    @staticmethod
    def authorization_from_decoded(decoded: ExternalItemType):
        scope = decoded.get("scope")
        scopes = tuple()
        if scope:
            scopes = scope.split(" ")
        authorization = Authorization(
            subject_id=decoded.get("sub"),
            not_before=date_from_jwt(decoded, "nbf"),
            expire_at=date_from_jwt(decoded, "exp"),
            scopes=frozenset(scopes),
        )
        return authorization


def date_from_jwt(decoded: ExternalItemType, key: str) -> Optional[datetime]:
    value = decoded.get(key)
    if value:
        return datetime.fromtimestamp(value)
