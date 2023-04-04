from servey.action.action import action
from servey.trigger.web_trigger import WEB_GET


def _generate(action_name: str):
    @action(name=action_name, triggers=WEB_GET)
    def my_action() -> str:
        return f"action_name was {action_name}"
    return my_action


generated_1 = _generate('generated_1')
generated_2 = _generate('generated_2')
generated_3 = _generate('generated_3')
