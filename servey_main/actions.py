from dataclasses import dataclass, field
from datetime import datetime
from time import sleep
from typing import Optional, List, ForwardRef

from servey.action.action import action
from servey.cache_control.ttl_cache_control import TtlCacheControl
from servey.action.example import Example
from servey.security.authorization import Authorization, ROOT
from servey.security.authorizer.authorizer_factory_abc import get_default_authorizer
from servey.servey_web_page.web_page_trigger import WebPageTrigger
from servey.trigger.fixed_rate_trigger import FixedRateTrigger
from servey.trigger.web_trigger import WEB_GET, WEB_POST


@action(
    triggers=(WEB_GET,),
    examples=(
        Example(
            name="usage", result="2022-12-04T15:32:33.843Z", include_in_tests=False
        ),
    ),
)
def current_time() -> datetime:
    """Get the current time on the server."""
    return datetime.now()


@action(
    triggers=(WEB_GET,),
    examples=(
        Example(name="usage", result=dict(scope=["root"]), include_in_tests=False),
    ),
)
def current_user_info(
    authorization: Optional[Authorization],
) -> Optional[Authorization]:
    """
    By default, authorization is derived from signed http headers - this just serves as a way
    of returning this info
    """
    return authorization


@action(triggers=(WEB_POST,))
def auth_token(username: str, password: str) -> Optional[str]:
    # Normally this would be some sort of database lookup - the below 3 lines is just for simplicity
    if username != "root" or password != "password":
        return None
    authorization = ROOT
    authorizer = get_default_authorizer()
    token = authorizer.encode(authorization)
    return token


@action(
    triggers=(WEB_GET,),
    examples=(Example(name="world", params=dict(name="World"), result="Hello World!"),),
)
def say_hello(name: str) -> str:
    """
    Hello world style demo function
    """
    return f"Hello {name}!"


@action(triggers=(WEB_GET,), cache_control=TtlCacheControl(30))
def slow_get_with_ttl() -> datetime:
    """
    This function demonstrates http caching with a slow function. The function will take 3 seconds to return, but
    the client should cache the results for 30 seconds.
    """
    sleep(3)
    return datetime.now()


@dataclass
class NumberStats:
    value: int

    @action
    async def factorial(self) -> int:
        """
        This demonstrates a resolvable field, lazily resolved (Usually by graphql)
        """
        result = 1
        index_ = self.value
        while index_ > 1:
            result *= index_
            index_ -= 1
        return result


@action(
    triggers=(WEB_GET,),
)
def number_stats(value: int) -> NumberStats:
    return NumberStats(value)


@action(triggers=(FixedRateTrigger(300),))
def ping():
    print("============== Ping! ==============")


@dataclass
class Node:
    """Demonstration of nested data structure"""

    name: str
    child_nodes: List[ForwardRef(f"{__name__}.Node")] = field(default_factory=list)

    @action
    def tree_size(self) -> int:
        result = 1 + sum(n.tree_size() for n in self.child_nodes)
        return result

    def get_node_by_name(self, name: str) -> Optional["Node"]:
        if name == self.name:
            return self
        for c in self.child_nodes:
            node = c.get_node_by_name(name)
            if node:
                return node


_ROOT = Node("root", [Node("child_a", [Node("grandchild_a")]), Node("child_b")])


@action(triggers=(WEB_GET,))
def get_node(path: str = "") -> Optional[Node]:
    node = _ROOT
    if path:
        path = path.split("/")
        for p in path:
            if p:
                node = next((n for n in node.child_nodes if n.name == p), None)
                if not node:
                    return None
    return node


@action(triggers=(WEB_GET,))
def get_node_by_name(name: str = "") -> Optional[Node]:
    node = _ROOT.get_node_by_name(name)
    return node


# noinspection PyUnusedLocal
@action(triggers=(WEB_POST,))
def put_root(node: Node) -> bool:
    global _ROOT
    _ROOT = node
    return True


# noinspection PyUnusedLocal
@action(triggers=(WEB_POST,))
def broadcast_message(message: str) -> bool:
    """Send a message to all connected users"""
    from servey_main.event_channels import messenger

    messenger.publish(message)
    return True


@dataclass
class PrintEvent:
    message: str
    count: int


# noinspection PyUnusedLocal
@action(triggers=(WEB_POST,))
def broadcast_print(message: str, count: int) -> bool:
    """Send a message to an action that will print to the console"""
    from servey_main.event_channels import printer

    printer.publish(PrintEvent(message, count))
    return True


@action
def print_consumer(event: PrintEvent):
    for _ in range(event.count):
        print(event.message)


@action(triggers=(WebPageTrigger(path="/"),))
def index():
    pass  # No model, no time


@action(triggers=(WebPageTrigger(),))
def current_time_page() -> datetime:
    return datetime.now()


def _generate(action_name: str):
    @action(name=action_name, triggers=WEB_GET)
    def my_action() -> str:
        return f"action_name was {action_name}"

    return my_action


generated_1 = _generate("generated_1")
generated_2 = _generate("generated_2")
generated_3 = _generate("generated_3")
