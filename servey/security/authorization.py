import inspect
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Set, FrozenSet, Callable

from marshy.factory.optional_marshaller_factory import get_optional_type


class AuthorizationError(Exception):
    pass


@dataclass(frozen=True)
class Authorization:
    # Probably a UUID - None implies some sort of headless access
    subject_id: Optional[str]
    scopes: FrozenSet[str]
    not_before: Optional[datetime]
    expire_at: Optional[datetime]

    def is_valid_for_timestamp(self, ts: Optional[datetime] = None):
        not_before = self.not_before
        expire_at = self.expire_at
        if not not_before and not expire_at:
            return True  # No timestamp specified
        if ts is None:
            ts = datetime.now()
        if not_before and ts < not_before:
            return False
        if expire_at and ts > expire_at:
            return False
        return True

    def has_scope(self, scope: str):
        has_scope = scope in self.scopes
        return has_scope

    def has_any_scope(self, scopes: Set[str]) -> bool:
        has_any = bool(self.scopes.intersection(scopes))
        return has_any

    def has_all_scopes(self, scopes: Set[str]) -> bool:
        has_all = self.scopes.issuperset(scopes)
        return has_all

    def check_valid_for_timestamp(self, ts: Optional[datetime] = None):
        if not self.is_valid_for_timestamp(ts):
            raise AuthorizationError(f"authorization_expired")

    def check_scope(self, scope: str):
        if not self.has_scope(scope):
            raise AuthorizationError(f"missing:{scope}")

    def check_any_scope(self, scopes: Set[str]):
        if not self.has_any_scope(scopes):
            raise AuthorizationError(f"missing_any:{scopes}")

    def check_all_scopes(self, scopes: Set[str]):
        if not self.has_all_scopes(scopes):
            raise AuthorizationError(f"missing_all:{self.scopes.difference(scopes)}")


# A default ROOT scope - rules may be adjusted to remove root access
ROOT = Authorization(None, frozenset(("root",)), None, None)
PUBLIC = Authorization(None, frozenset(), None, None)


def get_inject_at(fn: Callable) -> Optional[str]:
    sig = inspect.signature(fn)
    for p in sig.parameters.values():
        annotation = get_optional_type(p.annotation) or p.annotation
        if annotation == Authorization:
            return p.name
