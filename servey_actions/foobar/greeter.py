from dataclasses import dataclass
from typing import Optional, List

from servey.access_control.authorization import Authorization
from servey.action import action
from servey.trigger.web_trigger import WEB_GET


@action(triggers=(WEB_GET,))
def greet(name: str) -> str:
    """ Issue a greeting! """
    return f"Hello {name}"


@action
def about_me(authorization: Authorization) -> str:
    """ Give some info about the current authorization """
    return f"Your subject id is {authorization.subject_id} and your scopes are: {' '.join(authorization.scopes)}"


@action
class AlsoAboutMe:
    authorization: Optional[Authorization] = None

    def about_me(self) -> str:
        """ Give some info about the current authorization (Injected as a field rather than a kwarg) """
        return f"Your subject id is {self.authorization.subject_id} and your scopes are: {' '.join(self.authorization.scopes)}"


@dataclass
class Company:
    name: str
    domain: str
    year_founded: int


companies = []


@action(triggers=(WEB_GET,))
def list_companies() -> List[Company]:
    return companies


@action
def create_company(company: Company) -> Company:
    companies.append(company)
    return company
