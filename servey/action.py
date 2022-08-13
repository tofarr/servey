import asyncio
import inspect
from dataclasses import dataclass
from logging import getLogger
from typing import Callable, Optional, Tuple, Any

from marshy import get_default_context
from marshy.factory.optional_marshaller_factory import get_optional_type
from marshy.marshaller.marshaller_abc import MarshallerABC
from marshy.marshaller.obj_marshaller import ObjMarshaller, attr_config
from marshy.marshaller_context import MarshallerContext
from marshy.utils import resolve_forward_refs
from schemey import Schema, get_default_schema_context, SchemaContext

from servey.access_control.action_access_control_abc import ActionAccessControlABC
from servey.access_control.allow_all import ALLOW_ALL
from servey.access_control.authorization import Authorization
from servey.action_abc import ActionABC
from servey.action_meta import ActionMeta
from servey.servey_error import ServeyError
from servey.trigger.trigger_abc import TriggerABC
from servey.trigger.web_trigger import WebTrigger, WebTriggerMethod

logger = getLogger(__name__)


@dataclass(frozen=True)
class Action(ActionABC):
    """ General action, wraps a callable function, and allows authorization parameter to be optionally injected. """
    fn: Callable
    action_meta: ActionMeta
    params_marshaller: MarshallerABC
    result_marshaller: MarshallerABC
    authorization_inject_param: Optional[str] = None

    def __call__(self, authorization: Authorization, **kwargs) -> Any:
        self.pre_check(authorization, kwargs)
        if self.authorization_inject_param:
            kwargs[self.authorization_inject_param] = authorization
        result = self.fn(**kwargs)
        return result

    def invoke(self, authorization: Authorization, **kwargs) -> Any:
        """
        Invoke this action and return the result. Local actions do not strictly enforce
        timeouts, but will instead issue a warning to the logs. Environments like lambda
        are not so forgiving, and may leave data in an invalid state!
        """
        completed = False

        def timeout_check():
            if not completed:
                logger.error(f'action_ran_too_long:{self.action_meta.name}')

        loop = asyncio.get_event_loop()
        loop.call_later(self.action_meta.timeout, timeout_check)
        try:
            return self.__call__(authorization, **kwargs)
        finally:
            completed = True

    def invoke_async(self, authorization: Authorization, **kwargs):
        loop = asyncio.get_event_loop()
        loop.call_soon(lambda: self.invoke(authorization, **kwargs))

    def pre_check(self, authorization: Authorization, kwargs):
        if not self.action_meta.access_control.is_executable(authorization):
            raise ServeyError('insufficent_scopes')
        dumped_kwargs = self.params_marshaller.dump(kwargs)
        self.action_meta.params_schema.validate(dumped_kwargs)


def action(
    fn: Optional[Callable] = None,
    name: Optional[str] = None,
    params_schema: Optional[Schema] = None,
    params_marshaller: Optional[MarshallerABC] = None,
    result_schema: Optional[Schema] = None,
    result_marshaller: Optional[MarshallerABC] = None,
    access_control: ActionAccessControlABC = ALLOW_ALL,
    triggers: Tuple[TriggerABC, ...] = (WebTrigger(WebTriggerMethod.POST),),
    timeout: int = 30,
):
    """ Decorator which marks a global function as an action """

    def wrapper_(fn_: Callable):
        nonlocal name, params_schema, params_marshaller, result_schema, result_marshaller
        # Throw an error if the action is not global
        if not name:
            name = fn_.__name__
        if not params_schema:
            params_schema = get_schema_for_params(fn_)
        if not result_schema:
            result_schema = get_schema_for_result(fn_)
        if not params_marshaller:
            params_marshaller = get_marshaller_for_params(fn_)
        if not result_marshaller:
            result_marshaller = get_default_context().get_marshaller(result_schema.python_type)
        return Action(
            fn=fn_,
            action_meta=ActionMeta(
                name, params_schema, result_schema, access_control, triggers, timeout
            ),
            params_marshaller=params_marshaller,
            result_marshaller=result_marshaller,
            authorization_inject_param=get_authorization_inject_params(fn_)
        )

    return wrapper_ if fn is None else wrapper_(fn)


def get_schema_for_params(fn: Callable, schema_context: Optional[SchemaContext] = None) -> Schema:
    if not schema_context:
        schema_context = get_default_schema_context()
    sig = inspect.signature(fn)
    properties = {}
    required = []
    for p in list(sig.parameters.values()):
        if p.annotation is inspect.Parameter.empty:
            raise ServeyError(f'missing_param_annotation:{fn.__name__}({p.name}')
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


def get_marshaller_for_params(fn: Callable, marshaller_context: Optional[MarshallerContext] = None) -> MarshallerABC:
    if not marshaller_context:
        marshaller_context = get_default_context()
    sig = inspect.signature(fn)
    attr_configs = []
    for p in list(sig.parameters.values()):
        if p.annotation is inspect.Parameter.empty:
            raise ServeyError(f'missing_param_annotation:{fn.__name__}({p.name}')
        attr_configs.append(attr_config(marshaller_context.get_marshaller(p.annotation), p.name))
    marshaller = ObjMarshaller(dict, tuple(attr_configs))
    return marshaller


def get_schema_for_result(fn: Callable) -> Schema:
    schema_context = get_default_schema_context()
    sig = inspect.signature(fn)
    type_ = sig.return_annotation
    if type_ is inspect.Parameter.empty:
        raise ServeyError(f'missing_return_annotation:{fn.__name__}')
    schema = schema_context.schema_from_type(type_)
    return schema


def get_authorization_inject_params(fn: Callable) -> Optional[str]:
    sig = inspect.signature(fn)
    for p in list(sig.parameters.values()):
        if p.name != 'authorization':
            continue
        type_ = p.annotation
        type_ = get_optional_type(type_) or type_
        type_ = resolve_forward_refs(type_)
        if type_ == Authorization:
            return p.name
