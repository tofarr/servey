from dataclasses import dataclass
from typing import Optional

from servey.security.access_control.action_access_control_abc import (
    ActionAccessControlABC,
)
from servey.security.authorization import Authorization


@dataclass(frozen=True)
class PermissionAccessControl(ActionAccessControlABC):
    view_scope: str
    execute_scope: str

    def is_viewable(self, authorization: Optional[Authorization]) -> bool:
        return bool(authorization and self.view_scope) and authorization.has_scope(
            self.view_scope
        )

    def is_executable(self, authorization: Optional[Authorization]) -> bool:
        return bool(authorization and self.execute_scope) and authorization.has_scope(
            self.execute_scope
        )
