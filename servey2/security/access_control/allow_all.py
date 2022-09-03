from servey2.security.access_control.action_access_control_abc import (
    ActionAccessControlABC,
)
from servey2.security.authorization import Authorization
from servey2.util.singleton_abc import SingletonABC


class AllowAll(SingletonABC, ActionAccessControlABC):
    def is_viewable(self, authorization: Authorization) -> bool:
        return True

    def is_executable(self, authorization: Authorization) -> bool:
        return True


ALLOW_ALL = AllowAll()
