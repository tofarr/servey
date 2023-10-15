import inspect
from dataclasses import dataclass
from time import sleep
from typing import Callable


@dataclass
class Delayed:
    fn: Callable
    delay_seconds: int

    def __post_init__(self):
        # noinspection PyUnresolvedReferences
        sig = inspect.signature(self.fn)
        self.__signature__ = sig
        self.__name__ = self.fn.__name__

    def __call__(self, *args, **kwargs):
        sleep(self.delay_seconds)
        result = self.fn(*args, **kwargs)
        return result
