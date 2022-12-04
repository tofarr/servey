from datetime import datetime

from servey.action.action import action
from servey.action.trigger.web_trigger import WEB_GET
from servey.security.authorization import Authorization


@action(triggers=(WEB_GET,))
def current_time() -> datetime:
    """Get the current time on the server."""
    return datetime.now()


@action(triggers=(WEB_GET,))
def current_user_info(authorization: Authorization) -> Authorization:
    """
    By default, authorization is derived from signed http headers - this just serves as a way
    of returning this info
    """
    return authorization
