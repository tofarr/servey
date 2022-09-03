from dataclasses import dataclass
from typing import Optional

from marshy.types import ExternalItemType

from servey.access_control.authorization import Authorization, AuthorizationError
from servey.access_control.authorizer_abc import AuthorizerABC
from servey.action import Action
from servey.servey_error import ServeyError


@dataclass
class LambdaAction:
    action: Action
    authorizer: AuthorizerABC
    authorization_kwarg: Optional[str] = None
    authorization_field: Optional[str] = None

    def __call__(self, event: ExternalItemType, context):
        """Accepts Event in preset format and invokes action"""
        event_type = event.get("eventType")
        if event_type == "servey-1.0":
            return self.handle_event(event)
        elif event.get("httpMethod"):
            return self.handle_api_gateway_event(event)
        else:
            raise ServeyError("unknown_event_format")

    def handle_event(self, event: ExternalItemType):
        # Do we really need to add foo bar here?
        authorization = self.check_authorization(event)
        action = self.action
        params = event["params"]
        action.action_meta.params_schema.validate(params)
        kwargs = action.action_meta.params_marshaller.load(params)
        if self.authorization_kwarg:
            kwargs[self.authorization_kwarg] = authorization
        executor = action.create_executor()
        if self.authorization_field:
            setattr(executor.subject, self.authorization_field, authorization)
        result = executor.execute(**kwargs)
        dumped = action.action_meta.result_marshaller.dump(result)
        action.action_meta.params_schema.validate(dumped)
        return dumped

    def handle_api_gateway_event(self, event: ExternalItemType):
        web_trigger = self.web_trigger
        if not web_trigger:
            # This could only happen if somebody goes around the framework.
            # Fix it by adding a web trigger to the action
            raise ServeyError("non_web_triggered_lambda_from_api_gateway")
        authorization = event["headers"].get("Authorization")
        params = {}
        if web_trigger.method in BODY_METHODS:
            body = event.get("body")
            if body:
                params = json.loads(body)
        else:
            multi_value_query_string_parameters = event.get(
                "multiValueQueryStringParameters"
            )
            if multi_value_query_string_parameters:
                params = {
                    k: v[0] if len(v) == 1 else v
                    for k, v in multi_value_query_string_parameters.items()
                }
        return self.handle_event(dict(authorization=authorization, params=params))

    def check_authorization(self, event: ExternalItemType) -> Optional[Authorization]:
        authorization = None
        token = event.get("token")
        if token:
            authorization = self.authorizer.authorize(token)
        if not self.action.action_meta.access_control.is_executable(authorization):
            raise AuthorizationError("forbidden")
        return authorization


def handler(event, context):
    action = _get_action(context)
    authorizer = _get_authorizer()
    return LambdaMount(action, authorizer).handler(event)


def _get_action(context):
    global _ACTION
    if _ACTION:
        return _ACTION
    name = context.function_name.split("-")[-1]
    servey_action_path = os.environ.get("SERVEY_ACTION_PATH") or "servey_actions"
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
