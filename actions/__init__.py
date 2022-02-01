from datetime import datetime

from servey.wrapper import wrap_action


@wrap_action(path='/current-time')
def get_the_time() -> datetime:
    """ Get the current time """
    return datetime.now()

