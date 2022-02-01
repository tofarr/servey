from dataclasses import field, dataclass
from typing import Optional
from uuid import UUID, uuid4

from servey.http_method import HttpMethod
from servey.wrapper import wrap_action


@dataclass
class Item:
    id: UUID = field(default_factory=uuid4)
    title: str = ''


@wrap_action(http_methods=(HttpMethod.GET, HttpMethod.POST))
def say_hello(name: str) -> str:
    """ Say hello! """
    return f'Hello {name}'


@wrap_action
def get_item(id: Optional[UUID] = None) -> Item:
    if id is None:
        id = uuid4()
    return Item(id, 'Some Item')
