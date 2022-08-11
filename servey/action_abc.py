from abc import ABC
from typing import Any

from servey.access_control.authorization import Authorization


class ActionABC(ABC):
    """ Invoker for a (possibly remote) action. """

    def __call__(self, authorization: Authorization, **kwargs):
        return self.invoke(authorization, **kwargs)

    def invoke(self, authorization: Authorization, **kwargs) -> Any:
        """ Execute the action and await a response """

    def invoke_async(self, authorization: Authorization, **kwargs):
        """ Invoke the action but do not wait for a response """
