from dataclasses import dataclass, field
from typing import Generic, TypeVar, Dict

T = TypeVar("T")


@dataclass
class WebPageResponse(Generic[T]):
    model: T
    status_code: int = 200
    headers: Dict[str, str] = field(default_factory=dict)
