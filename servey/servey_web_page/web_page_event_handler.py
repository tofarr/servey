import asyncio
import inspect
from dataclasses import field, dataclass
from typing import Optional, Any, Awaitable

from jinja2 import PackageLoader, Environment
from marshy import get_default_context
from marshy.marshaller_context import MarshallerContext
from marshy.types import ExternalItemType
from schemey import get_default_schema_context, SchemaContext

from servey.action.action import Action
from servey.action.util import get_marshaller_for_params, get_schema_for_params
from servey.security.access_control.allow_all import ALLOW_ALL
from servey.security.authorizer.authorizer_abc import AuthorizerABC
from servey.security.authorizer.authorizer_factory_abc import get_default_authorizer
from servey.servey_aws.event_handler.api_gateway_event_handler import (
    ApiGatewayEventHandler,
)
from servey.servey_aws.event_handler.event_handler import separate_auth_kwarg
from servey.servey_aws.event_handler.event_handler_abc import (
    EventHandlerABC,
    EventHandlerFactoryABC,
)
from servey.servey_web_page.web_page_trigger import WebPageTrigger, get_environment


@dataclass
class WebPageEventHandler(ApiGatewayEventHandler):
    template_name: Optional[str] = None

    @property
    def template(self):
        template = getattr(self, "_template", None)
        if not template:
            template = get_environment().get_template(self.template_name)
            setattr(self, "_template", template)
        return template

    def handle(self, event: ExternalItemType, result: Any) -> ExternalItemType:
        kwargs = self.parse_kwargs(event)
        result = self.action.fn(**kwargs)
        if isinstance(result, Awaitable):
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(result)
        dumped = self.result_marshaller.dump(result)
        body = self.template.render(model=dumped)
        response = {
            "statusCode": 200,
            "headers": {"Content-Type": "text/html"},
            "body": body,
        }
        self.apply_caching(event, response)
        return response


@dataclass
class WebPageEventHandlerFactory(EventHandlerFactoryABC):
    marshaller_context: MarshallerContext = field(default_factory=get_default_context)
    schema_context: SchemaContext = field(default_factory=get_default_schema_context)
    auth_kwarg_name: Optional[str] = None
    authorizer: Optional[AuthorizerABC] = None
    validate_output: bool = True
    priority: int = 110

    def create(self, action: Action) -> Optional[EventHandlerABC]:
        trigger = next(
            (t for t in action.triggers if isinstance(t, WebPageTrigger)), None
        )
        if not trigger:
            return

        fn, auth_kwarg_name = separate_auth_kwarg(action.fn)
        param_marshaller = get_marshaller_for_params(fn, set(), self.marshaller_context)
        result_marshaller = None
        param_schema = get_schema_for_params(fn, set(), self.schema_context)
        result_schema = None
        sig = inspect.signature(fn)
        if sig.return_annotation != inspect.Signature.empty:
            result_marshaller = self.marshaller_context.get_marshaller(
                sig.return_annotation
            )
            if self.validate_output:
                result_schema = self.schema_context.schema_from_type(
                    sig.return_annotation
                )
        authorizer = (
            get_default_authorizer()
            if auth_kwarg_name or action.access_control != ALLOW_ALL
            else None
        )
        return WebPageEventHandler(
            action=action,
            param_marshaller=param_marshaller,
            param_schema=param_schema,
            result_marshaller=result_marshaller,
            result_schema=result_schema,
            auth_kwarg_name=auth_kwarg_name,
            authorizer=authorizer,
            priority=self.priority,
            template_name=trigger.template_name or f"{action.name}.j2",
        )
