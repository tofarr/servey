from servey.action.action import get_action
from servey.security.access_control.allow_none import ALLOW_NONE
from servey.subscription.subscription import subscription
from servey_main.actions import PrintEvent, print_consumer

messager = subscription(str, "messager")


printer = subscription(
    PrintEvent,
    "printer",
    access_control=ALLOW_NONE,
    action_subscribers=(get_action(print_consumer),),
)
