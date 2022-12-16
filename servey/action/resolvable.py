import dataclasses
from typing import Callable, Optional

from servey.cache_control.cache_control_abc import CacheControlABC
from servey.security.access_control.action_access_control_abc import (
    ActionAccessControlABC,
)
from servey.security.access_control.allow_all import ALLOW_ALL


@dataclasses.dataclass(frozen=True)
class Resolvable:
    """
    Marker indicating that a method on an object returned from a handler is optionally resolvable. This typically
    represents the case where a graphql client can request particular fields to be resolved or not
    """

    fn: Callable
    access_control: ActionAccessControlABC = (ALLOW_ALL,)
    cache_control: Optional[CacheControlABC] = (None,)


def resolvable(
    fn: Optional[Callable],
    access_control: ActionAccessControlABC = ALLOW_ALL,
    cache_control: Optional[CacheControlABC] = None,
):
    """Decorator for resolvable fields"""

    def wrapper_(fn_: Callable):
        fn_.__servey_resolvable__ = Resolvable(fn_, access_control, cache_control)
        return fn_

    return wrapper_ if fn is None else wrapper_(fn)


def get_resolvable(fn: Callable) -> Optional[Resolvable]:
    return getattr(fn, "__servey_resolvable__", None)
