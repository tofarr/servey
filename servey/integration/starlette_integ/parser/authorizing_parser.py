from dataclasses import dataclass, field
from typing import Tuple, Optional, Dict, Any

from marshy.types import ExternalItemType
from starlette.requests import Request

from servey.access_control.allow_all import ALLOW_ALL
from servey.access_control.authorization import AuthorizationError
from servey.access_control.authorizer_abc import AuthorizerABC
from servey.access_control.authorizer_factory_abc import get_default_authorizer
from servey.access_control.filter import (
    get_authorization_field_name,
    get_authorization_kwarg_name, action_without_kwarg,
)
from servey.action import Action
from servey.executor import Executor
from servey.integration.starlette_integ.parser.parser_abc import (
    ParserABC,
    ParserFactoryABC,
)
from servey.trigger.web_trigger import WebTrigger


@dataclass
class AuthorizingParser(ParserABC):
    """
    Parser which pulls kwargs from a request body
    """

    action: Action
    authorizer: AuthorizerABC
    parser: ParserABC
    field_name: Optional[str]
    kwarg_name: Optional[str]

    async def parse(self, request: Request) -> Tuple[Executor, Dict[str, Any]]:
        authorization = self.get_authorization(request)
        if not self.action.action_meta.access_control.is_executable(authorization):
            raise AuthorizationError()
        executor, kwargs = await self.parser.parse(request)
        if self.field_name:
            setattr(executor.subject, self.field_name, authorization)
        if self.kwarg_name:
            kwargs[self.kwarg_name] = authorization
        return executor, kwargs

    def get_authorization(self, request: Request):
        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            return
        token = token[7:]
        return self.authorizer.authorize(token)

    def to_openapi_schema(
        self, path_method: ExternalItemType, components: ExternalItemType
    ):
        responses: ExternalItemType = path_method['responses']
        if not responses.get("403"):
            responses["403"] = {"description": "Unauthorized"}
        if not path_method.get("security"):
            path_method["security"] = [{"OAuth2PasswordBearer": []}]
        if not components.get('securitySchemas'):
            components['securitySchemes'] = {
                'OAuth2PasswordBearer': {
                    'type': "oauth2",
                    'flows': {
                        'password': {
                            'scopes': {},
                            'tokenUrl': "/login"
                        }
                    }
                }
            }


@dataclass
class AuthorizingParserFactory(ParserFactoryABC):
    priority: int = 80
    authorizer: AuthorizerABC = field(default_factory=get_default_authorizer)
    ignore: bool = False

    def create(
        self,
        action: Action,
        trigger: WebTrigger,
        parser_factories: Tuple[ParserFactoryABC],
    ) -> Optional[ParserABC]:
        if self.ignore:
            return
        field_name = get_authorization_field_name(action)
        kwarg_name = get_authorization_kwarg_name(action)
        if (
            action.action_meta.access_control == ALLOW_ALL
            and not field_name
            and not kwarg_name
        ):
            return
        wrapped_action = action
        if kwarg_name:
            wrapped_action = action_without_kwarg(action, kwarg_name)

        self.ignore = True
        try:
            for factory in parser_factories:
                parser = factory.create(wrapped_action, trigger, parser_factories)
                if parser:
                    return AuthorizingParser(
                        action, self.authorizer, parser, field_name, kwarg_name
                    )
        finally:
            self.ignore = False
