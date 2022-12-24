from dataclasses import dataclass
from typing import Optional


@dataclass
class ErrorResponse:
    """Content definition for error response"""

    error_code: str
    error_msg: Optional[str] = None
