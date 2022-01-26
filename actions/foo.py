from servey import ActionType
from servey import wrap_action


@wrap_action(action_type=ActionType.GET)
def get_hello(name: str) -> str:
    return f'Hello {name}'


@wrap_action
def post_hello(name: str) -> str:
    return f'Hello {name}'

