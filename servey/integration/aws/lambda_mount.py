"""
This package holds a mount point for a lambda. It uses the name of the lambda from the context to try and find
an associated action.

Code generation may be a viable alternative to this package
"""
import json
import os
from dataclasses import dataclass
from logging import getLogger
from typing import Dict, Optional

from marshy.factory.impl_marshaller_factory import get_impls

from servey.access_control.authorization import AuthorizationError, Authorization
from servey.access_control.authorizer_abc import AuthorizerABC
from servey.access_control.authorizer_factory_abc import AuthorizerFactoryABC, create_authorizer
from servey.action import Action
from servey.action_finder import find_actions
from servey.servey_error import ServeyError
from servey.trigger.web_trigger import WebTrigger, WebTriggerMethod

PARAMS_METHODS = (
    WebTriggerMethod.DELETE,
    WebTriggerMethod.GET,
    WebTriggerMethod.HEAD,
    WebTriggerMethod.OPTIONS
)
LOGGER = getLogger(__name__)


@dataclass
class LambdaMount:
    action: Action
    authorizer: AuthorizerABC
    web_trigger: Optional[WebTrigger] = None

    def __post_init__(self):
        if not self.web_trigger:
            self.web_trigger = next((
                t for t in self.action.action_meta.triggers
                if isinstance(t, WebTrigger)
            ), None)

    def handler(self, event, context):
        event_type = event.get('eventType')
        if event_type == 'servey.1.0':
            return self.handle_event(event)
        elif event.get('httpMethod'):
            return self.handle_api_gateway_event(event)
        else:
            raise ServeyError('unknown_event_format')

    def handle_event(self, event: Dict):
        authorization = self.check_authorization(event)
        action = self.action
        params = event['params']
        action.action_meta.params_schema.validate(params)
        params = action.params_marshaller.load(params)
        if action.authorization_inject_param:
            params[action.authorization_inject_param] = authorization
        result = action.fn(**params)
        result = action.result_marshaller.dump(result)
        action.action_meta.params_schema.validate(result)
        return result

    def handle_api_gateway_event(self, event: Dict):
        web_trigger = self.web_trigger
        if not web_trigger:
            # This could only happen if somebody goes around the framework.
            # Fix it by adding a web trigger to the action
            raise ServeyError('non_web_triggered_lambda_from_api_gateway')
        authorization = event['headers'].get('Authorization')
        params = {}
        if web_trigger.method in PARAMS_METHODS:
            multi_value_query_string_parameters = event.get('multiValueQueryStringParameters')
            if multi_value_query_string_parameters:
                params = {
                    k: v[0] if len(v) == 1 else v
                    for k, v in multi_value_query_string_parameters.items()
                }
        else:
            body = event.get('body')
            if body:
                params = json.loads(body)
        return self.handle_event(dict(
            authorization=authorization,
            params=params
        ))

    def check_authorization(self, event: Dict) -> Authorization:
        authorization = event['authorization']
        authorization = self.authorizer.authorize(authorization)
        if not self.action.action_meta.access_control.is_executable(authorization):
            raise AuthorizationError('forbidden')
        return authorization


def handler(event, context):
    action = _get_action(context)
    authorizer = _get_authorizer()
    return LambdaMount(action, authorizer).handler(event)


def _get_action(context):
    global _ACTION
    if _ACTION:
        return _ACTION
    name = context.function_name.split('-')[-1]
    servey_action_path = os.environ.get('SERVEY_ACTION_PATH') or 'servey_actions'
    for found_action in find_actions([servey_action_path]):
        action = found_action.action
        if action.action_meta.name == name:
            _ACTION = action
            return action


def _get_authorizer() -> AuthorizerABC:
    global _AUTHORIZER
    if not _AUTHORIZER:
        _AUTHORIZER = create_authorizer()
    return _AUTHORIZER


_ACTION = None
_AUTHORIZER = None
