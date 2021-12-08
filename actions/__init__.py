from datetime import datetime

from servey.action_type import ActionType
from servey.wrapper import wrap_action


@wrap_action(action_type=ActionType.GET)
def get_the_time() -> datetime:
    return datetime.now()

