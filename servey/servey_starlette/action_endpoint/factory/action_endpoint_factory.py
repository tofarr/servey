import inspect
from dataclasses import field, dataclass
from typing import List, Optional, Set

from marshy import get_default_context
from marshy.marshaller_context import MarshallerContext
from schemey import get_default_schema_context, SchemaContext

from servey.action.action import Action
from servey.action.util import get_marshaller_for_params, get_schema_for_params
from servey.errors import ServeyError
from servey.servey_starlette.action_endpoint.action_endpoint import ActionEndpoint
from servey.servey_starlette.action_endpoint.action_endpoint_abc import (
    ActionEndpointABC,
)
from servey.servey_starlette.action_endpoint.factory.action_endpoint_factory_abc import (
    ActionEndpointFactoryABC,
)
from servey.trigger.web_trigger import WebTrigger


@dataclass
class ActionEndpointFactory(ActionEndpointFactoryABC):
    priority: int = 100
    marshaller_context: MarshallerContext = field(default_factory=get_default_context)
    schema_context: SchemaContext = field(default_factory=get_default_schema_context)
    validate_output: bool = True
    path_pattern: str = "/actions/{action_name}"

    def create(
        self,
        action: Action,
        skip_args: Set[str],
        factories: List[ActionEndpointFactoryABC],
    ) -> Optional[ActionEndpointABC]:
        web_triggers = [t for t in action.triggers if isinstance(t, WebTrigger)]
        if web_triggers:
            methods = {t.method for t in web_triggers}
            paths = {t.path for t in web_triggers if t.path}
            if len(paths) == 1:
                path = next(iter(paths))
            elif len(paths) > 1:
                raise ServeyError(
                    f"multi_paths_not_supported:{action.name}:{','.join(paths)}"
                )
            else:
                path = self.path_pattern.format(
                    action_name=action.name.replace("_", "-")
                )
            result_type = inspect.signature(action.fn).return_annotation
            if result_type == inspect.Signature.empty:
                raise ServeyError(f"missing_return_type:{action.fn}")
            endpoint = ActionEndpoint(
                action=action,
                path=path,
                methods=tuple(methods),
                params_marshaller=get_marshaller_for_params(
                    action.fn, skip_args, self.marshaller_context
                ),
                params_schema=get_schema_for_params(
                    action.fn, skip_args, self.schema_context
                ),
                result_marshaller=self.marshaller_context.get_marshaller(result_type),
                result_schema=self.schema_context.schema_from_type(result_type)
                if self.validate_output
                else None,
            )
            return endpoint
