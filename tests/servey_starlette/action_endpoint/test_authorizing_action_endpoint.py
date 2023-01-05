import asyncio
import json
import os
from unittest import TestCase
from unittest.mock import patch

from servey.action.action import action, get_action
from servey.security.access_control.scope_access_control import ScopeAccessControl
from servey.security.authorization import Authorization, ROOT
from servey.security.authorizer.authorizer_factory_abc import get_default_authorizer
from servey.servey_starlette.route_factory.action_route_factory import (
    ActionRouteFactory,
)
from servey.servey_starlette.route_factory.openapi_route_factory import (
    OpenapiRouteFactory,
)
from servey.trigger.web_trigger import WEB_GET
from tests.servey_starlette.action_endpoint.test_action_endpoint import build_request


class TestAuthorizingActionEndpoint(TestCase):
    def test_valid_input_get(self):
        @action(triggers=(WEB_GET,), access_control=ScopeAccessControl("root"))
        def echo_get(val: str, auth: Authorization) -> str:
            return " ".join(auth.scopes) + ": " + val

        with (
            patch(
                "servey.servey_starlette.route_factory.action_route_factory.find_actions",
                return_value=[get_action(echo_get)],
            ),
            patch(
                "servey.servey_starlette.route_factory.openapi_route_factory.find_actions",
                return_value=[get_action(echo_get)],
            ),
            patch.dict(os.environ, {"SERVER_HOST": "https://testy.com"}),
        ):
            routes = list(ActionRouteFactory().create_routes())
            openapi_routes = list(OpenapiRouteFactory().create_routes())
            self.assertEqual(1, len(routes))
            self.assertEqual(2, len(openapi_routes))
            loop = asyncio.get_event_loop()

            # Unauthorized
            request = build_request(query_string="val=bar")
            response = loop.run_until_complete(routes[0].endpoint(request))
            self.assertEqual(401, response.status_code)
            self.assertEqual(dict(error="unauthorized"), json.loads(response.body))

            # Authorized
            authorizer = get_default_authorizer()
            token = authorizer.encode(ROOT)
            request = build_request(
                query_string="val=bar",
                headers=dict(Authorization=f"Bearer {token}"),
            )
            response = loop.run_until_complete(routes[0].endpoint(request))
            self.assertEqual(200, response.status_code)
            self.assertEqual("root: bar", json.loads(response.body))

            request = build_request()
            response = openapi_routes[0].endpoint(request)
            self.assertEqual(200, response.status_code)
            schema = json.loads(response.body)
            expected_schema = {
                "components": {
                    "ErrorResponse": {
                        "additionalProperties": False,
                        "description": "Content definition for error response",
                        "name": "ErrorResponse",
                        "properties": {
                            "error_code": {"type": "string"},
                            "error_msg": {
                                "anyOf": [{"type": "string"}, {"type": "null"}],
                                "default": None,
                            },
                        },
                        "required": ["error_code"],
                        "type": "object",
                    },
                    "securitySchemes": {
                        "OAuth2PasswordBearer": {
                            "flows": {"password": {"scopes": {}, "tokenUrl": "/login"}},
                            "type": "oauth2",
                        }
                    },
                },
                "info": {"title": "Servey", "version": "0.1.0"},
                "openapi": "3.0.2",
                "paths": {
                    "/actions/echo-get": {
                        "get": {
                            "operationId": "echo_get",
                            "parameters": [
                                {
                                    "in": "query",
                                    "name": "val",
                                    "required": True,
                                    "schema": {"type": "string"},
                                }
                            ],
                            "responses": {
                                "200": {
                                    "content": {
                                        "application/json": {
                                            "schema": {"type": "string"}
                                        }
                                    },
                                    "description": "Successful Response",
                                },
                                "403": {
                                    "content": {
                                        "application/json": {
                                            "schema": {
                                                "$ref": "#components/ErrorResponse"
                                            }
                                        }
                                    },
                                    "description": "unauthorized",
                                },
                                "422": {"description": "Validation " "Error"},
                            },
                            "security": [{"OAuth2PasswordBearer": []}],
                        }
                    }
                },
                "servers": [{"url": "https://testy.com"}],
            }
            self.assertEqual(expected_schema, schema)
