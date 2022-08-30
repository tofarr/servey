from __future__ import annotations

import inspect
from dataclasses import dataclass
from logging import getLogger
from typing import Callable, Optional, Tuple, Union, Type, Generic, TypeVar

from marshy import get_default_context
from marshy.marshaller.marshaller_abc import MarshallerABC
from marshy.marshaller.obj_marshaller import ObjMarshaller, attr_config
from marshy.marshaller_context import MarshallerContext
from schemey import Schema, get_default_schema_context, SchemaContext

from servey.access_control.action_access_control_abc import ActionAccessControlABC
from servey.access_control.allow_all import ALLOW_ALL
from servey.action_meta import ActionMeta
from servey.executor import Executor
from servey.servey_error import ServeyError
from servey.trigger.trigger_abc import TriggerABC
from servey.trigger.web_trigger import WebTrigger, WebTriggerMethod
from servey.util import to_snake_case

logger = getLogger(__name__)
T = TypeVar("T")


@dataclass(frozen=True)
class Action(Generic[T]):
    action_meta: ActionMeta
    subject: Union[Type, Callable]

    @property
    def method_name(self):
        return getattr(self.subject, "__servey_method_name__", None)

    def get_signature(self) -> inspect.Signature:
        method_name = self.method_name
        fn = getattr(self.subject, method_name) if method_name else self.subject
        sig = inspect.signature(fn)
        params = list(sig.parameters.values())
        if method_name:
            params = params[1:]
        sig = sig.replace(parameters=tuple(params))
        return sig

    def create_executor(self) -> Executor:
        if inspect.isclass(self.subject):
            subject = self.subject()
        else:
            subject = self.subject
        return Executor(subject, self.method_name)


def action(
    cls_or_fn: Optional[Callable] = None,
    name: Optional[str] = None,
    method_name: Optional[str] = None,
    params_schema: Optional[Schema] = None,
    params_marshaller: Optional[MarshallerABC] = None,
    result_schema: Optional[Schema] = None,
    result_marshaller: Optional[MarshallerABC] = None,
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

    def wrapper_(cls_or_fn_: Callable):
        if inspect.isclass(cls_or_fn_):
            return wrap_class(cls_or_fn_)
        elif callable(cls_or_fn_):
            return wrap_fn(cls_or_fn_)
        else:
            raise TypeError(cls_or_fn_)

    def wrap_class(cls):
        nonlocal method_name
        cls = dataclass(cls)
        name_ = name or to_snake_case(cls.__name__)
        if method_name:
            fn = getattr(cls, method_name)
        else:
            fns = [
                v
                for k, v in cls.__dict__.items()
                if not k.startswith("_") and callable(v)
            ]
            if len(fns) == 1:
                fn = fns[0]
                method_name = fn.__name__
            else:
                raise ValueError(f"multiple_methods_found:{cls}")
        cls.__servey_action_meta__ = get_meta_for_fn(name_, fn, True)
        cls.__servey_method_name__ = method_name
        return cls

    def wrap_fn(fn):
        if method_name:
            raise ValueError(
                f"defining_method_name_while_wrapping_function:{method_name}"
            )
        fn.__servey_action_meta__ = get_meta_for_fn(fn.__name__, fn, False)
        return fn

    def get_meta_for_fn(name_: str, fn: Callable, bound: bool):
        nonlocal params_schema, params_marshaller, result_schema, result_marshaller
        if not params_schema:
            params_schema = get_schema_for_params(fn, bound)
        if not result_schema:
            result_schema = get_schema_for_result(fn)
        if not params_marshaller:
            params_marshaller = get_marshaller_for_params(fn, bound)
        if not result_marshaller:
            result_marshaller = get_default_context().get_marshaller(
                result_schema.python_type
            )
        return ActionMeta(
            name=name_,
            description=fn.__doc__,
            params_marshaller=params_marshaller,
            params_schema=params_schema,
            result_marshaller=result_marshaller,
            result_schema=result_schema,
            access_control=access_control,
            triggers=triggers,
            timeout=timeout,
        )

    return wrapper_ if cls_or_fn is None else wrapper_(cls_or_fn)


def get_schema_for_params(
    fn: Callable, bound: bool, schema_context: Optional[SchemaContext] = None
) -> Schema:
    if not schema_context:
        schema_context = get_default_schema_context()
    sig = inspect.signature(fn)
    properties = {}
    required = []
    params = list(sig.parameters.values())
    if bound:
        params = params[1:]
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


def get_marshaller_for_params(
    fn: Callable, bound: bool, marshaller_context: Optional[MarshallerContext] = None
) -> MarshallerABC:
    if not marshaller_context:
        marshaller_context = get_default_context()
    sig = inspect.signature(fn)
    attr_configs = []
    params = list(sig.parameters.values())
    if bound:
        params = params[1:]
    for p in params:
        if p.annotation is inspect.Parameter.empty:
            raise ServeyError(f"missing_param_annotation:{fn.__name__}({p.name}")
        attr_configs.append(
            attr_config(marshaller_context.get_marshaller(p.annotation), p.name)
        )
    marshaller = ObjMarshaller(dict, tuple(attr_configs))
    return marshaller


def get_schema_for_result(fn: Callable) -> Schema:
    schema_context = get_default_schema_context()
    sig = inspect.signature(fn)
    type_ = sig.return_annotation
    if type_ is inspect.Parameter.empty:
        raise ServeyError(f"missing_return_annotation:{fn.__name__}")
    schema = schema_context.schema_from_type(type_)
    return schema
