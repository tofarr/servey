from servey.security.access_control.access_control_abc import (
    AccessControlABC,
)
from servey.security.authorization import Authorization
from servey.util.singleton_abc import SingletonABC


class AllowNone(SingletonABC, AccessControlABC):
    def is_executable(self, authorization: Authorization) -> bool:
        return False


ALLOW_NONE = AllowNone()
