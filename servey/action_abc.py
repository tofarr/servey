from abc import ABC, abstractmethod

from servey.executor_abc import ExecutorABC


class ActionABC(ABC):
    """Definition for an action"""

    @abstractmethod
    def create_executor(self) -> ExecutorABC:
        """Create a subject for this action."""


"""
@action
class GreeterAction:

    def __call__(self, name: str) -> Any:
        return f"Hello {name}!"

greeting = GreeterAction()('Tim')

@action(method_name='get_current_user')
class CurrentUserAction(ActionABC):
    username: str

    def get_current_user(self) -> str:
        return username

current_username = CurrentUserAction().get_curent_user()

@action
def get_the_time() -> datetime
    return datetime.now()


now = get_the_time()
"""
