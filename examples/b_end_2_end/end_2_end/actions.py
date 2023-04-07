from servey.action.action import action
from servey.trigger.web_trigger import WEB_GET


@action(triggers=WEB_GET)
def say_hello(name: str) -> str:
    return f"Hello {name}!"
