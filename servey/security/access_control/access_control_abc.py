from abc import ABC, abstractmethod
from typing import Optional

from servey.security.authorization import Authorization


class AccessControlABC(ABC):
    @abstractmethod
    def is_executable(self, authorization: Optional[Authorization]) -> bool:
        """Determine if this action_ may be executed using the authorization given"""
