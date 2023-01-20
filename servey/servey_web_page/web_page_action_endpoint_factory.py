import inspect
from dataclasses import field, dataclass
from typing import Set, List, Optional

from marshy import get_default_context
from marshy.marshaller_context import MarshallerContext
from schemey import SchemaContext, get_default_schema_context

from servey.action.action import Action
from servey.action.util import get_marshaller_for_params, get_schema_for_params
from servey.errors import ServeyError
from servey.servey_starlette.action_endpoint.action_endpoint_abc import (
    ActionEndpointABC,
)
from servey.servey_starlette.action_endpoint.factory.action_endpoint_factory_abc import (
    ActionEndpointFactoryABC,
)
from servey.servey_web_page.web_page_action_endpoint import WebPageActionEndpoint
from servey.servey_web_page.web_page_trigger import WebPageTrigger


@dataclass
class WebPageActionEndpointFactory(ActionEndpointFactoryABC):
    """
    Factory for endpoints using templates
    """

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
        triggers = [t for t in action.triggers if isinstance(t, WebPageTrigger)]
        if not triggers:
            return
        if len(triggers) > 1:
            raise ServeyError(f"multi_triggers_not_supported:{triggers}")
        trigger = triggers[0]
        path = trigger.path or f"/{action.name.replace('_', '-')}"
        result_type = inspect.signature(action.fn).return_annotation
        if result_type == inspect.Signature.empty:
            result_type = None
        endpoint = WebPageActionEndpoint(
            action=action,
            path=path,
            methods=(trigger.method,),
            params_marshaller=get_marshaller_for_params(
                action.fn, skip_args, self.marshaller_context
            ),
            params_schema=get_schema_for_params(
                action.fn, skip_args, self.schema_context
            ),
            result_marshaller=self.marshaller_context.get_marshaller(result_type)
            if result_type
            else None,
            result_schema=self.schema_context.schema_from_type(result_type)
            if self.validate_output and result_type
            else None,
            template_name=trigger.template_name,
        )
        return endpoint
