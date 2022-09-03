import inspect
from typing import Optional, Callable, Tuple

from schemey import Schema, SchemaContext, get_default_schema_context

from servey.servey_error import ServeyError
from servey2.action.action_meta import ActionMeta
from servey2.security.access_control.action_access_control_abc import (
    ActionAccessControlABC,
)
from servey2.security.access_control.allow_all import ALLOW_ALL
from servey2.action.trigger.trigger_abc import TriggerABC
from servey2.action.trigger.web_trigger import WebTrigger, WebTriggerMethod


def action(
    fn: Optional[Callable] = None,
    params_schema: Optional[Schema] = None,
    result_schema: Optional[Schema] = None,
    access_control: ActionAccessControlABC = ALLOW_ALL,
    triggers: Tuple[TriggerABC, ...] = (WebTrigger(WebTriggerMethod.POST),),
    timeout: int = ActionMeta.timeout,
):
    """
    Decorator for actions, which may be a function or a class with a designated method_name
    to act as the action. This decorator doesn't really do anything special aside from
    adding metadata to the object which may be interpreted when the action is mounted.

    When mounting, operations like security checks and validations are performed, as well as
    parameter injection for class based actions.
    """

    def wrapper_(fn_: Callable):
        fn_.__servey_action_meta__ = get_meta_for_fn(fn_.__name__, fn_)
        return fn_

    def get_meta_for_fn(name_: str, fn: Callable):
        nonlocal params_schema, result_schema
        if not params_schema:
            params_schema = get_schema_for_params(fn)
        if not result_schema:
            result_schema = get_schema_for_result(fn)
        return ActionMeta(
            name=name_,
            description=fn.__doc__,
            params_schema=params_schema,
            result_schema=result_schema,
            access_control=access_control,
            triggers=triggers,
            timeout=timeout,
        )

    return wrapper_ if fn is None else wrapper_(fn)


def get_schema_for_params(
    fn: Callable, schema_context: Optional[SchemaContext] = None
) -> Schema:
    if not schema_context:
        schema_context = get_default_schema_context()
    sig = inspect.signature(fn)
    properties = {}
    required = []
    params = list(sig.parameters.values())
    for p in params:
        if p.annotation is inspect.Parameter.empty:
            raise ServeyError(f"missing_param_annotation:{fn.__name__}:{p.name}")
        properties[p.name] = schema_context.schema_from_type(p.annotation).schema
        if p.default == inspect.Parameter.empty:
            required.append(p.name)
    json_schema = {
        "type": "object",
        "properties": properties,
        "additionalProperties": False,
        "required": required,
    }
    schema = Schema(json_schema, dict)
    return schema


def get_schema_for_result(fn: Callable) -> Schema:
    schema_context = get_default_schema_context()
    sig = inspect.signature(fn)
    type_ = sig.return_annotation
    if type_ is inspect.Parameter.empty:
        raise ServeyError(f"missing_return_annotation:{fn.__name__}")
    schema = schema_context.schema_from_type(type_)
    return schema
