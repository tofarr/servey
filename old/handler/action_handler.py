import inspect
import re
from dataclasses import dataclass
import logging
from http import HTTPStatus
from typing import Callable, Optional, Iterable, Iterator, Any

from marshy import get_default_context
from marshy.marshaller.marshaller_abc import MarshallerABC
from marshy.marshaller.obj_marshaller import ObjMarshaller, attr_config
from marshy.marshaller_context import MarshallerContext
from schemey.object_schema import ObjectSchema
from schemey.property_schema import PropertySchema
from schemey.schema_abc import SchemaABC
from schemey.schema_context import SchemaContext, get_default_schema_context

from old.handler.action_type import ActionType
from old.handler.handler_abc import HandlerABC
from old.request import Request
from old.response import Response

logger = logging.getLogger(__name__)
STARTS_WITH_UNDERSCORE = re.compile('_.*$')


@dataclass(frozen=True)
class ActionHandler(HandlerABC):
    name: str
    doc: Optional[str]
    callable: Callable
    params_marshaller: MarshallerABC
    return_marshaller: MarshallerABC
    params_schema: ObjectSchema
    return_schema: SchemaABC
    action_type: ActionType

    def match(self, request: Request) -> bool:
        matched = request.method == 'POST' and request.path[-1] == self.name
        return matched

    def handle_request(self, request: Request) -> Response:
        kwargs = self.params_marshaller.load(request.params)
        self.params_schema.validate(kwargs)
        result = self.callable(**kwargs)
        self.return_schema.validate(result)
        dumped = self.return_marshaller.dump(result)
        return Response(HTTPStatus.OK, dumped)


def action_handler(callable_: Callable,
                   marshaller_context: Optional[MarshallerContext],
                   schema_context: Optional[SchemaContext],
                   action_type: ActionType = None
                   ) -> ActionHandler:
    action_handler_ = ActionHandler(
        name=callable_.__name__,
        doc=callable_.__doc__,
        callable=callable_,
        params_marshaller=build_params_marshaller(callable_, marshaller_context),
        return_marshaller=build_return_marshaller(callable_, marshaller_context),
        params_schema=build_params_schema(callable_, schema_context),
        return_schema=build_return_schema(callable_, schema_context),
        action_type=action_type or get_action_type_from_name(callable_.__name__)
    )
    return action_handler_


def get_action_type_from_name(name: str):
    if name.startswith('get') or name.startswith('read') or name.startswith('list'):
        return ActionType.QUERY
    else:
        return ActionType.MUTATION

def generate_action_handlers(app_object: Any,
                             exclude_functions: Iterable[re.Pattern] = (STARTS_WITH_UNDERSCORE,)
                             ) -> Iterator[ActionHandler]:
    for name in dir(app_object):
        match = next((e for e in exclude_functions if e.match(name)), None)
        if match:
            continue
        value = getattr(app_object, name)
        if not callable(value):
            continue

        def callable_(**kwargs):
            result = value(app_object, **kwargs)
            return result

        action_handler_ = ActionHandler(name=name,
                                        callable=callable_,
                                        doc=value.__doc__,
                                        params_marshaller=build_params_marshaller(value),
                                        return_marshaller=build_return_marshaller(value),
                                        params_schema=build_params_schema(value),
                                        return_schema=build_return_schema(value),
                                        action_type=get_action_type_from_name(name))
        yield action_handler_
