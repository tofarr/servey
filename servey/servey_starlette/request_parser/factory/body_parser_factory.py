import inspect
from dataclasses import field, dataclass
from typing import List, Optional, Callable

from marshy import get_default_context
from marshy.marshaller.marshaller_abc import MarshallerABC
from marshy.marshaller.obj_marshaller import attr_config, ObjMarshaller
from marshy.marshaller_context import MarshallerContext

from servey.action.finder.found_action import FoundAction
from servey.action.trigger.web_trigger import WebTrigger, BODY_METHODS
from servey.servey_starlette.request_parser.body_parser import BodyParser
from servey.servey_starlette.request_parser.factory.request_parser_factory_abc import RequestParserFactoryABC
from servey.servey_starlette.request_parser.request_parser_abc import RequestParserABC


@dataclass
class BodyParserFactory(RequestParserFactoryABC):
    marshaller_context: MarshallerContext = field(default_factory=get_default_context)
    priority: int = 50

    def create(
        self,
        action: FoundAction,
        trigger: WebTrigger,
        parser_factories: List[RequestParserFactoryABC],
    ) -> Optional[RequestParserABC]:
        if trigger.method in BODY_METHODS:
            return BodyParser(
                schema=action.action_meta.params_schema,
                marshaller=get_marshaller_for_params(action.fn, self.marshaller_context)
            )


def get_marshaller_for_params(
    fn: Callable, marshaller_context: Optional[MarshallerContext] = None
) -> MarshallerABC:
    if not marshaller_context:
        marshaller_context = get_default_context()
    sig = inspect.signature(fn)
    attr_configs = []
    params = list(sig.parameters.values())
    for p in params:
        if p.annotation is inspect.Parameter.empty:
            raise TypeError(f"missing_param_annotation:{fn.__name__}({p.name}")
        attr_configs.append(
            attr_config(marshaller_context.get_marshaller(p.annotation), p.name)
        )
    marshaller = ObjMarshaller(dict, tuple(attr_configs))
    return marshaller
