from asyncio import get_event_loop
from dataclasses import dataclass
from unittest import TestCase

from servey.action.action import action, get_action
from servey.servey_starlette.action_endpoint.factory.action_endpoint_factory import (
    ActionEndpointFactory,
)
from servey.servey_starlette.action_endpoint.factory.self_action_endpoint_factory import (
    SelfActionEndpointFactory,
)
from servey.trigger.web_trigger import WEB_GET
from tests.servey_starlette.action_endpoint.test_action_endpoint import build_request


class TestSelfActionEndpoint(TestCase):
    def test_self(self):
        action_ = get_action(Foo.zap)
        factories = [SelfActionEndpointFactory(), ActionEndpointFactory()]
        endpoint = factories[0].create(action_, set(), factories)
        schema = {"paths": {}, "components": {}}
        endpoint.to_openapi_schema(schema)
        expected_schema = {
            "paths": {
                "/actions/zap": {
                    "get": {
                        "responses": {
                            "422": {"description": "Validation Error"},
                            "200": {
                                "description": "Successful Response",
                                "content": {
                                    "application/json": {"schema": {"type": "integer"}}
                                },
                            },
                        },
                        "operationId": "zap",
                        "parameters": [
                            {
                                "required": True,
                                "schema": {"type": "integer"},
                                "name": "self.bar",
                                "in": "query",
                            },
                            {
                                "required": True,
                                "schema": {"type": "integer"},
                                "name": "bang",
                                "in": "query",
                            },
                        ],
                    }
                }
            },
            "components": {},
        }
        self.assertEqual(expected_schema, schema)
        request = build_request(query_string="self.bar=1&bang=2")
        loop = get_event_loop()
        result = loop.run_until_complete(endpoint.execute(request))
        self.assertEqual(b"3", result.body)


@dataclass
class Foo:
    bar: int

    @action(triggers=(WEB_GET,))
    def zap(self, bang: int) -> int:
        return self.bar + bang
