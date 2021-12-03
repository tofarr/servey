from abc import ABC
import re
from typing import Iterable, Optional, Callable, Dict

from servey.client.http_callable import http_callable

STARTS_WITH_UNDERSCORE = re.compile('_.*$')


class HttpServiceClientABC(ABC):
    """
    Simply wrapping functions in http_callable comes with the downside of losing some code completion in some IDEs
    (Pycharm). Putting the functions in a service class has the advantage of grouping similar things together
    and maintaining all code completion (hoodwinking the IDE ;)
    """
    __root_url__: str
    __exclude_functions__: Iterable[re.Pattern] = (STARTS_WITH_UNDERSCORE,)
    __header_factory__: Optional[Callable[[], Dict[str, str]]] = None

    def __init_subclass__(cls, **kwargs):
        """
        When a subclass is initialized, run through each of its attributes and connect them to the remote service
        """
        for name in dir(cls):
            match = next((e for e in cls.__exclude_functions__ if e.match(name)), None)
            if match:
                continue
            callable_ = getattr(cls, name)
            wrapper = http_callable(f'{cls.__root_url__}{name}')
            callable_ = staticmethod(wrapper(callable_))
            setattr(cls, name, callable_)
