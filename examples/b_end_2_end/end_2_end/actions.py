from end_2_end.models import IndexModel
from servey.action.action import action
from servey.servey_web_page.web_page_trigger import WebPageTrigger
from servey.trigger.web_trigger import WEB_GET


@action(triggers=WEB_GET)
def say_hello(name: str) -> str:
    return f"Hello {name}!"


@action(triggers=WebPageTrigger(path='/'))
def index() -> IndexModel:
    return IndexModel()
