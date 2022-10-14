from dataclasses import dataclass
from typing import List

from servey.action.action import action
from servey.action.trigger.web_trigger import WEB_GET
from servey.security.authorization import Authorization


@action(triggers=(WEB_GET,))
def greet(name: str) -> str:
    """Issue a greeting!"""
    return f"Hello {name}"


@action
def about_me(authorization: Authorization) -> str:
    """Give some info about the current authorization"""
    return f"Your subject id is {authorization.subject_id} and your scopes are: {' '.join(authorization.scopes)}"


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
