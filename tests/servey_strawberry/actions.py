from datetime import datetime

from servey.action.action import action
from servey.trigger.web_trigger import WEB_GET


@action(triggers=(WEB_GET,))
def get_the_time() -> datetime:
    """This is a dummy"""
