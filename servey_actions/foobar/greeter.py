from typing import Optional

from servey.access_control.authorization import Authorization
from servey.action import action


@action
def greet(name: str) -> str:
    return f"Hello {name}"


@action
def about_me(authorization: Authorization) -> str:
    return f"Your subject id is {authorization.subject_id} and your scopes are: {' '.join(authorization.scopes)}"


@action
class AlsoAboutMe:
    authorization: Optional[Authorization] = None

    def about_me(self) -> str:
        return f"Your subject id is {self.authorization.subject_id} and your scopes are: {' '.join(self.authorization.scopes)}"
