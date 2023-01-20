import asyncio
import inspect
import json
from dataclasses import field, dataclass
from email.utils import parsedate_to_datetime
from typing import Optional, Any, Awaitable

from marshy import get_default_context, ExternalType
from marshy.marshaller_context import MarshallerContext
from marshy.types import ExternalItemType
from schemey import get_default_schema_context, SchemaContext

from servey.action.action import Action
from servey.action.util import get_marshaller_for_params, get_schema_for_params
from servey.security.access_control.allow_all import ALLOW_ALL
from servey.security.authorization import AuthorizationError, Authorization
from servey.security.authorizer.authorizer_abc import AuthorizerABC
from servey.security.authorizer.authorizer_factory_abc import get_default_authorizer
from servey.servey_aws.event_handler.event_handler import (
    separate_auth_kwarg,
    EventHandler,
)
from servey.servey_aws.event_handler.event_handler_abc import (
    EventHandlerABC,
    EventHandlerFactoryABC,
)


class ApiGatewayEventHandler(EventHandler):
    def is_usable(self, event: ExternalItemType, context) -> bool:
        return "httpMethod" in event

    def parse_kwargs(self, event: ExternalItemType) -> ExternalType:
        if event.get("httpMethod") in ("POST", "PATCH", "PUT"):
            params = json.loads(event.get("body") or "{}")
        else:
            params = event.get("queryStringParameters") or {}
        path_parameters = event.get("pathParameters")
        if path_parameters:
            params.update(path_parameters)
        if self.param_schema:
            self.param_schema.validate(params)
        kwargs = self.param_marshaller.load(params)
        if self.auth_kwarg_name or self.action.access_control != ALLOW_ALL:
            authorization = self.get_authorization(event)
            if not self.action.access_control.is_executable(authorization):
                raise AuthorizationError("unauthorized")
            if self.auth_kwarg_name:
                kwargs[self.auth_kwarg_name] = authorization
        return kwargs

    def get_authorization(self, event: ExternalItemType) -> Optional[Authorization]:
        headers = event.get("headers") or {}
        token = (headers.get("Authorization") or "").strip()
        if not token or not token.startswith("Bearer "):
            return
        token = token[7:]
        return self.authorizer.authorize(token)

    def handle(self, event: ExternalItemType, result: Any) -> ExternalItemType:
        kwargs = self.parse_kwargs(event)
        result = self.action.fn(**kwargs)
        if isinstance(result, Awaitable):
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(result)
        dumped = self.result_marshaller.dump(result)
        response = {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(dumped),
        }
        self.apply_caching(event, response)
        return response

    def apply_caching(self, event: ExternalItemType, response: ExternalItemType):
        if self.action.cache_control:
            headers = event.get("headers") or {}
            if_match = headers.get("If-Match")
            if_modified_since = headers.get("If-Modified-Since")
            cache_header = self.action.cache_control.get_cache_header_from_content(
                response["body"]
            )
            response["headers"].update(cache_header.get_http_headers())
            if if_match and cache_header.etag:
                if cache_header.etag == if_match:
                    response["statusCode"] = 304
                    response["body"] = ""
            elif if_modified_since and cache_header.updated_at:
                if_modified_since_date = parsedate_to_datetime(if_modified_since)
                if (
                    if_modified_since_date.timestamp()
                    >= cache_header.updated_at.timestamp()
                ):
                    response["statusCode"] = 304
                    response["body"] = ""


@dataclass
class ApiGatewayEventHandlerFactory(EventHandlerFactoryABC):
    marshaller_context: MarshallerContext = field(default_factory=get_default_context)
    schema_context: SchemaContext = field(default_factory=get_default_schema_context)
    auth_kwarg_name: Optional[str] = None
    authorizer: Optional[AuthorizerABC] = None
    validate_output: bool = True
    priority: int = 100

    def create(self, action: Action) -> EventHandlerABC:
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
        return ApiGatewayEventHandler(
            action=action,
            param_marshaller=param_marshaller,
            param_schema=param_schema,
            result_marshaller=result_marshaller,
            result_schema=result_schema,
            auth_kwarg_name=auth_kwarg_name,
            authorizer=authorizer,
            priority=self.priority,
        )
