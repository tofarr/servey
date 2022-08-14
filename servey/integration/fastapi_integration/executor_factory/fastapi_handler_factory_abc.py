from abc import ABC, abstractmethod
from typing import Callable, Optional, Tuple

from fastapi import FastAPI
from marshy.factory.impl_marshaller_factory import get_impls

from servey.action import Action
from servey.trigger.web_trigger import WebTrigger


class FastapiHandlerFactoryABC(ABC):
    priority: int = 100

    @abstractmethod
    def create_handler_for_action(
        self, action: Action, trigger: WebTrigger
    ) -> Optional[Callable]:
        """
        Create an executor instance. This pluggable mechanism determines
        how fastapi will interface with actions
        """

    @abstractmethod
    def mount_dependencies(self, api: FastAPI):
        """
        Mount any dependencies which may have been incurred by mounting handlers
        (e.g.: Authentication)
        """


def create_fastapi_handler_factories() -> Tuple[FastapiHandlerFactoryABC, ...]:
    impls = get_impls(FastapiHandlerFactoryABC)
    impls = [impl() for impl in impls]
    impls.sort(key=lambda f: f.priority, reverse=True)
    return tuple(impls)
