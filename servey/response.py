from dataclasses import dataclass, field
from http import HTTPStatus
from typing import Dict, Optional, Union


@dataclass
class Response:
    code: Union[HTTPStatus, int]
    headers: Dict[str, str] = field(default_factory=dict)
    content: Optional[str] = None
