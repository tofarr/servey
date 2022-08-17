import inspect
from inspect import Signature
from typing import Tuple

from fastapi import FastAPI, Body
from fastapi.params import Depends
from pydantic.fields import Undefined

from servey.action import Action
from servey.integration.fastapi_integration.handler_filter.fastapi_handler_filter_abc import (
    ExecutorFn,
    FastapiHandlerFilterABC,
)
from servey.trigger.web_trigger import WebTrigger, BODY_METHODS


class BodyHandlerFilter(FastapiHandlerFilterABC):
    """
    Update filter which defaults to have all parameters grabbed from the request body
    for POST, PUT and PATCH requests (rather than query parameters)
    """

    priority: int = 90

    def filter(
        self, action: Action, trigger: WebTrigger, fn: ExecutorFn, sig: Signature
    ) -> Tuple[ExecutorFn, Signature, bool]:
        if trigger.method not in BODY_METHODS:
            return fn, sig, True
        params = []
        for param in sig.parameters.values():
            default = param.default
            if not isinstance(default, Depends):
                if default is inspect.Parameter.empty:
                    default = Undefined
                param = param.replace(default=Body(embed=True, default=default))
            params.append(param)
        sig = sig.replace(parameters=params)
        return fn, sig, True

    def mount_dependencies(self, api: FastAPI):
        # No dependencies required
        pass
