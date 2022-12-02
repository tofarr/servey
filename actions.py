from datetime import datetime

from servey.action.action import action
from servey.action.trigger.web_trigger import WEB_GET


@action(triggers=(WEB_GET,))
def current_time() -> datetime:
    """ Get the current time on the server. """
    return datetime.now()
