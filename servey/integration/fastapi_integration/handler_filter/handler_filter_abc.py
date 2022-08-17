from abc import ABC, abstractmethod
from inspect import Signature
from typing import Callable, Tuple, Dict, Any, List

from fastapi import FastAPI

from servey.action import Action
from servey.executor import Executor
from servey.trigger.web_trigger import WebTrigger

ExecutorFn = Callable[[Executor, Dict[str, Any]], Any]


class HandlerFilterABC(ABC):
    """
    Sometimes the default behaviour from fastapi is not quite what we want, so this allows us to customize
    how a http request will be passed to an action.
    Examples include adding authorization and authentication and reading parameters from a POST body rather
    than a URL query string.
    """

    priority: int = 100

    @abstractmethod
    def filter(
        self, action: Action, trigger: WebTrigger, fn: ExecutorFn, sig: Signature
    ) -> Tuple[ExecutorFn, Signature, bool]:
        """Filter the action given. The callable is a function"""

    @abstractmethod
    def mount_dependencies(self, api: FastAPI):
        """Mount any routes required for this filter"""


def create_handler_filters() -> Tuple[HandlerFilterABC]:
    from marshy.factory.impl_marshaller_factory import get_impls
    filters: List[HandlerFilterABC] = [f() for f in get_impls(HandlerFilterABC)]
    filters.sort(key=lambda f: f.priority, reverse=True)
    return tuple(filters)
