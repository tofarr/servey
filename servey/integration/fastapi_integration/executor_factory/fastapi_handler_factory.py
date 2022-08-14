import inspect
from inspect import Signature
from typing import Optional, Callable

from fastapi import FastAPI, Body
from pydantic.fields import Undefined

from servey.action import Action
from servey.integration.fastapi_integration.executor_factory.fastapi_handler_factory_abc import (
    FastapiHandlerFactoryABC,
)
from servey.trigger.web_trigger import WebTrigger, WebTriggerMethod


class FastapiHandlerFactory(FastapiHandlerFactoryABC):
    """
    Standard implementation of factory for executorable instances.
    """

    priority: int = 50

    def create_handler_for_action(
        self, action: Action, trigger: WebTrigger
    ) -> Optional[Callable]:
        sig = action.get_signature()

        if trigger.method in (WebTriggerMethod.PATCH, WebTriggerMethod.POST, WebTriggerMethod.PUT):
            sig = params_from_body(sig)

        def handle(**kwargs):
            executor = action.create_executor()
            result = executor.execute(**kwargs)
            return result

        handle.__name__ = action.action_meta.name
        handle.__signature__ = sig
        return handle

    def mount_dependencies(self, api: FastAPI):
        pass  # This has no dependencies


def params_from_body(sig: Signature) -> Signature:
    parameters = []
    for p in sig.parameters.values():
        default = p.default
        if default is inspect.Parameter.empty:
            default = Undefined
        parameters.append(p.replace(default=Body(embed=True, default=default)))
    return sig.replace(parameters=parameters)
