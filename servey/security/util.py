import inspect
from dataclasses import is_dataclass, fields
from typing import Callable, Optional

from marshy.factory.optional_marshaller_factory import get_optional_type

from servey.security.authorization import Authorization


def get_inject_at(fn: Callable) -> Optional[str]:
    sig = inspect.signature(fn)
    for p in sig.parameters.values():
        annotation = get_optional_type(p.annotation) or p.annotation
        if annotation == Authorization:
            return p.name
