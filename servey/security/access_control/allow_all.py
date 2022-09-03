from servey.security.access_control.action_access_control_abc import (
    ActionAccessControlABC,
)
from servey.security.authorization import Authorization
from servey.util.singleton_abc import SingletonABC


class AllowAll(SingletonABC, ActionAccessControlABC):
    def is_viewable(self, authorization: Authorization) -> bool:
        return True

    def is_executable(self, authorization: Authorization) -> bool:
        return True


ALLOW_ALL = AllowAll()
