from dataclasses import dataclass
from typing import Optional


@dataclass
class ErrorResponse:
    error_code: str
    error_msg: Optional[str] = None
