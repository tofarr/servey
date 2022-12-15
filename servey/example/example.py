from dataclasses import field, dataclass
from typing import Optional

from marshy import ExternalType
from marshy.types import ExternalItemType


@dataclass
class Example:
    """Example invocation which may be used for mocks and unit testing."""

    name: str
    params: ExternalItemType = field(default_factory=dict)
    result: ExternalType = None
    description: Optional[str] = None
    include_in_tests: bool = True
    include_in_schema: bool = True
