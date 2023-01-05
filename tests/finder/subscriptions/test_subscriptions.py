from dataclasses import dataclass

from servey.subscription.subscription import subscription


@dataclass
class MyEvent:
    msg: str


my_subscription = subscription(MyEvent)
