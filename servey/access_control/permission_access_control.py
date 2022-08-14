from dataclasses import dataclass

from servey.access_control.action_access_control_abc import ActionAccessControlABC
from servey.access_control.authorization import Authorization


@dataclass(frozen=True)
class PermissionAccessControl(ActionAccessControlABC):
    view_scope: str
    execute_scope: str

    def is_viewable(self, authorization: Authorization) -> bool:
        return bool(self.view_scope) and authorization.has_scope(self.view_scope)

    def is_executable(self, authorization: Authorization) -> bool:
        return bool(self.execute_scope) and authorization.has_scope(self.execute_scope)
