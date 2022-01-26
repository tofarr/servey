from datetime import datetime

from servey.wrapper import wrap_action


@wrap_action
def get_the_time() -> datetime:
    return datetime.now()

