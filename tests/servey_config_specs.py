from typing import Optional

from old.handler import app_handler, merged_app_handler
from old.handler.handler_abc import HandlerABC

priority = 100


def configure_handler(handler: Optional[HandlerABC]) -> HandlerABC:
    return merged_app_handler(handler, app_handler(GreetingService()))


class GreetingService():

    def say_hello(self, name: str = 'Doofus') -> str:
        """ Return a greeting for the named user given! """
        return f'Hello {name}!'
