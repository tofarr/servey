import inspect
from dataclasses import dataclass
from typing import Dict, Callable, Optional


@dataclass(frozen=True)
class Resolver:
    """ Resolver for use in graphql to match functions to top level objects. """
    action_name: str
    kwarg_mappings: Dict[str, str]
    batch_action_name: str
    batch_kwarg_mappings: Dict[str, str]


def resolver(
        fn: Callable,
        action_name: Optional[str] = None,
        kwarg_mappings: Optional[Dict[str, str]] = None,
        batch_action_name: Optional[str] = None,
        batch_kwarg_mappings: Optional[Dict[str, str]] = None
):
    def wrapper_(fn_: Callable):
        nonlocal action_name, kwarg_mappings, batch_kwarg_mappings
        if not action_name:
            action_name = fn_.__name__
        if not kwarg_mappings:
            kwarg_mappings = {}
        if not batch_kwarg_mappings:
            batch_kwarg_mappings = {}
        sig = inspect.signature(fn_)
        for param in sig.parameters:
            if param.name not in kwarg_mappings:
                kwarg_mappings[param.name] = param.name
        fn_._servey_resolver__ = Resolver(action_name, kwarg_mappings, batch_action_name, batch_kwarg_mappings)
        return fn_

    return wrapper_ if fn is None else wrapper_(fn)
