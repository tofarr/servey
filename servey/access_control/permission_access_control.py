from dataclasses import dataclass

from servey.access_control.action_access_control_abc import ActionAccessControlABC
from servey.access_control.authorization import Authorization


@dataclass(frozen=True)
class PermissionAccessControl(ActionAccessControlABC):
    view_permission: str
    execute_permission: str

    def is_viewable(self, authorization: Authorization) -> bool:
        return bool(self.view_permission) and authorization.has_permission(
            self.view_permission
        )

    def is_executable(self, authorization: Authorization) -> bool:
        return bool(self.execute_permission) and authorization.has_permission(
            self.execute_permission
        )
