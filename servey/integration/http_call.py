import inspect
from dataclasses import dataclass
from typing import Any, Optional, Dict, Callable
from urllib.parse import urlencode
import requests
from marshy import get_default_context
from marshy.factory.optional_marshaller_factory import get_optional_type

from marshy.marshaller.marshaller_abc import MarshallerABC
from schemey import Schema

from servey.access_control.authorization import Authorization
from servey.access_control.authorizer_abc import AuthorizerABC
from servey.action import get_marshaller_for_params, get_schema_for_params, get_schema_for_result
from servey.servey_error import ServeyError
from servey.trigger.web_trigger import WebTriggerMethod

URL_PARAMS_METHODS = (WebTriggerMethod.GET, WebTriggerMethod.DELETE, WebTriggerMethod.OPTIONS, WebTriggerMethod.HEAD)

@dataclass
class HttpCall:
    """Remote invocation of an action over http."""
    url: str
    param_schema: Schema
    param_marshaller: MarshallerABC
    result_schema: Schema
    result_marshaller: MarshallerABC
    method: WebTriggerMethod = WebTriggerMethod.POST
    authorizer: Optional[AuthorizerABC] = None
    authorization_arg: Optional[str] = None

    def __call__(self, **kwargs):
        response = self.get_response(kwargs)
        if response.status_code != 200:
            raise ServeyError(response.text)
        result = response.json
        self.result_schema.validate(result)
        result = self.result_marshaller.load(result)
        return result

    def call_async(self, **kwargs):
        self.get_response(kwargs)

    def get_response(self, kwargs: Dict[str, Any]) -> Any:
        params = self.param_marshaller.dump(kwargs)
        self.param_schema.validate(params)
        method = getattr(requests, self.method.value)
        if self.method in URL_PARAMS_METHODS:
            return method(
                f"{self.url}?{urlencode(params)}",
                auth=self.auth_to_header(kwargs),
            )
        else:
            return method(
                self.url, auth=self.auth_to_header(kwargs), json=params
            )

    def auth_to_header(self, kwargs: Dict[str, Any]) -> Optional[str]:
        """Convert the authorization given to a header"""
        if self.authorizer and self.authorization_arg:
            authorization = kwargs[self.authorization_arg]
            if authorization:
                return self.authorizer.encode(authorization)


def http_action(
    fn: Optional[Callable],
    url: str,
    param_schema: Optional[Schema] = None,
    param_marshaller: Optional[MarshallerABC] = None,
    result_schema: Optional[Schema] = None,
    result_marshaller: Optional[MarshallerABC] = None,
    method: str = HttpCall.method,
    authorizer: Optional[AuthorizerABC] = None
):
    """ 
    Take a function (typically just a mock and convert it into a remote http action
    """
    def wrapper(fn_):
        nonlocal param_schema, param_marshaller, result_schema, result_marshaller
        sig = inspect.signature(fn_)
        if not param_schema:
            param_schema = get_schema_for_params(fn, False)
        if not param_marshaller:
            param_marshaller = get_marshaller_for_params(fn, False)
        if not result_schema:
            result_schema = get_schema_for_result(fn)
        if not result_marshaller:
            result_marshaller = get_default_context().get_marshaller(
                result_schema.python_type
            )
        authorization_arg = None
        if authorizer:
            authorization_arg = get_authorization_arg(sig)
        call = HttpCall(
            url=url,
            param_schema=param_schema,
            param_marshaller=param_marshaller,
            result_schema=result_schema,
            result_marshaller=result_marshaller,
            method=method,
            authorizer=authorizer,
            authorization_arg=authorization_arg
        )
        call.__call__.__signature__ = sig
        return call
    return wrapper  # Always has args - at least URL!


def get_authorization_arg(sig: inspect.Signature) -> Optional[str]:
    for param in sig.parameters.values():
        type_ =  param.annotation
        if (get_optional_type(type_) or type_) == Authorization:
            return param.name
