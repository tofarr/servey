from dataclasses import dataclass
from typing import Optional

from servey.security.access_control.access_control_abc import (
    AccessControlABC,
)
from servey.security.authorization import Authorization


@dataclass(frozen=True)
class ScopeAccessControl(AccessControlABC):
    execute_scope: Optional[str]

    def is_executable(self, authorization: Optional[Authorization]) -> bool:
        return bool(authorization and self.execute_scope) and authorization.has_scope(
            self.execute_scope
        )
