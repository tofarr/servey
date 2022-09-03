from abc import ABC
from typing import Optional

from servey.security.authorization import Authorization


class ActionAccessControlABC(ABC):
    def is_viewable(self, authorization: Optional[Authorization]) -> bool:
        """Determine if this action's meta may be viewed using the outhorization given"""

    def is_executable(self, authorization: Optional[Authorization]) -> bool:
        """Determine if this action may be executed using the outhorization given"""
