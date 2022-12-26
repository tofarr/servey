import asyncio
import json
from datetime import datetime
from unittest import TestCase

from starlette.datastructures import Headers
from starlette.exceptions import HTTPException
from starlette.requests import Request, empty_receive

from servey.action.action import action, get_action
from servey.action.example import Example
from servey.errors import ServeyError
from servey.servey_starlette.action_endpoint.factory.action_endpoint_factory import (
    ActionEndpointFactory,
)
from servey.trigger.web_trigger import WEB_GET, WEB_POST
from tests.servey_strawberry.test_schema_factory import Node


class TestActionEndpoint(TestCase):
    def test_valid_input_get(self):
        @action(triggers=(WEB_GET,))
        def echo_get(val: str) -> str:
            return val

        action_endpoint = ActionEndpointFactory().create(
            get_action(echo_get), set(), []
        )
        request = build_request(query_string=b"val=bar")
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(action_endpoint.execute(request))
        self.assertEqual(200, response.status_code)
        self.assertEqual("bar", json.loads(response.body))

    def test_valid_input_post(self):
        @action(triggers=(WEB_POST,))
        def echo_get(val: str) -> str:
            return val

        action_endpoint = ActionEndpointFactory().create(
            get_action(echo_get), set(), []
        )
        request = build_request(method="POST", body=json.dumps(dict(val="bar")))
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(action_endpoint.execute(request))
        self.assertEqual(200, response.status_code)
        self.assertEqual("bar", json.loads(response.body))

    def test_invalid_input(self):
        # noinspection PyUnusedLocal
        @action(triggers=(WEB_GET,))
        def echo_get(val: int) -> int:
            """This is never invoked"""

        action_endpoint = ActionEndpointFactory().create(
            get_action(echo_get), set(), []
        )
        request = build_request(query_string="val=bar")
        loop = asyncio.get_event_loop()
        with self.assertRaises(HTTPException):
            loop.run_until_complete(action_endpoint.execute(request))

    def test_invalid_input_post(self):
        # noinspection PyUnusedLocal
        @action(triggers=(WEB_POST,))
        def echo_get(val: int) -> int:
            """This is never invoked"""

        action_endpoint = ActionEndpointFactory().create(
            get_action(echo_get), set(), []
        )
        request = build_request(method="POST", body="""{"val":"bar"}""")
        loop = asyncio.get_event_loop()
        with self.assertRaises(HTTPException):
            loop.run_until_complete(action_endpoint.execute(request))

    def test_invalid_output(self):
        @action(triggers=(WEB_GET,))
        def echo_get() -> int:
            # noinspection PyTypeChecker
            return "foobar"

        action_endpoint = ActionEndpointFactory().create(
            get_action(echo_get), set(), []
        )
        request = build_request()
        loop = asyncio.get_event_loop()
        with self.assertRaises(HTTPException):
            loop.run_until_complete(action_endpoint.execute(request))
        action_endpoint.result_schema = None
        loop.run_until_complete(action_endpoint.execute(request))

    def test_get_route(self):
        @action(triggers=(WEB_GET,))
        def dummy() -> datetime:
            """dummy route"""

        action_ = get_action(dummy)
        action_endpoint = ActionEndpointFactory().create(action_, set(), [])
        route = action_endpoint.get_route()
        self.assertEqual("dummy", route.name)
        self.assertEqual("/actions/dummy", route.path)
        self.assertEqual({"GET", "HEAD"}, set(route.methods))

    def test_open_api_get(self):
        @action(
            triggers=(WEB_GET,),
            examples=(
                Example(
                    "standard",
                    params=dict(id="id", value=1.2, count=3, flag=True),
                    result="2022-12-01 00:00:00+00:00",
                    description="Standard invocation of dummy",
                ),
            ),
        )
        def dummy(id: str, value: float, count: int, flag: bool = True) -> datetime:
            """dummy route"""

        action_ = get_action(dummy)
        action_endpoint = ActionEndpointFactory().create(action_, set(), [])
        schema = dict(paths={}, components={})
        action_endpoint.to_openapi_schema(schema)
        expected_schema = {
            "components": {},
            "paths": {
                "/actions/dummy": {
                    "get": {
                        "operationId": "dummy",
                        "parameters": [
                            {
                                "examples": {
                                    "standard": {
                                        "summary": "Standard "
                                        "invocation "
                                        "of "
                                        "dummy",
                                        "value": "id",
                                    }
                                },
                                "in": "query",
                                "name": "id",
                                "required": True,
                                "schema": {"type": "string"},
                            },
                            {
                                "examples": {
                                    "standard": {
                                        "summary": "Standard "
                                        "invocation "
                                        "of "
                                        "dummy",
                                        "value": 1.2,
                                    }
                                },
                                "in": "query",
                                "name": "value",
                                "required": True,
                                "schema": {"type": "number"},
                            },
                            {
                                "examples": {
                                    "standard": {
                                        "summary": "Standard "
                                        "invocation "
                                        "of "
                                        "dummy",
                                        "value": 3,
                                    }
                                },
                                "in": "query",
                                "name": "count",
                                "required": True,
                                "schema": {"type": "integer"},
                            },
                            {
                                "examples": {
                                    "standard": {
                                        "summary": "Standard "
                                        "invocation "
                                        "of "
                                        "dummy",
                                        "value": True,
                                    }
                                },
                                "in": "query",
                                "name": "flag",
                                "required": False,
                                "schema": {"type": "boolean"},
                            },
                        ],
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "examples": {
                                            "standard": {
                                                "summary": "Standard "
                                                "invocation "
                                                "of "
                                                "dummy",
                                                "value": "2022-12-01 " "00:00:00+00:00",
                                            }
                                        },
                                        "schema": {
                                            "format": "date-time",
                                            "type": "string",
                                        },
                                    }
                                },
                                "description": "Successful " "Response",
                            },
                            "422": {"description": "Validation " "Error"},
                        },
                        "summary": "dummy route",
                    }
                }
            },
        }
        self.assertEqual(expected_schema, schema)

    def test_open_api_post(self):
        @action(
            triggers=(WEB_POST,),
            examples=(
                Example(
                    "standard",
                    params=dict(node=dict(name="Foo")),
                    result=dict(name="Foo", child_nodes=[]),
                    description="Standard invocation of dummy",
                ),
            ),
        )
        def dummy(node: Node) -> Node:
            """dummy route"""

        action_ = get_action(dummy)
        action_endpoint = ActionEndpointFactory().create(action_, set(), [])
        schema = dict(paths={}, components={})
        action_endpoint.to_openapi_schema(schema)
        expected_schema = {
            "components": {
                "Node": {
                    "additionalProperties": False,
                    "description": "Node(name: str, child_nodes: "
                    "List[ForwardRef('tests.servey_strawberry.test_schema_factory.Node')] "
                    "= <factory>)",
                    "name": "Node",
                    "properties": {
                        "child_nodes": {
                            "items": {"$ref": "#/components/Node"},
                            "type": "array",
                        },
                        "name": {"type": "string"},
                    },
                    "required": ["name"],
                    "type": "object",
                }
            },
            "paths": {
                "/actions/dummy": {
                    "post": {
                        "operationId": "dummy",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "examples": {
                                        "standard": {
                                            "summary": "Standard "
                                            "invocation "
                                            "of "
                                            "dummy",
                                            "value": {"node": {"name": "Foo"}},
                                        }
                                    },
                                    "schema": {
                                        "additionalProperties": False,
                                        "properties": {
                                            "node": {"$ref": "#/components/Node"}
                                        },
                                        "required": ["node"],
                                        "type": "object",
                                    },
                                }
                            },
                            "required": True,
                        },
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "examples": {
                                            "standard": {
                                                "summary": "Standard "
                                                "invocation "
                                                "of "
                                                "dummy",
                                                "value": {
                                                    "child_nodes": [],
                                                    "name": "Foo",
                                                },
                                            }
                                        },
                                        "schema": {"$ref": "#/components/Node"},
                                    }
                                },
                                "description": "Successful " "Response",
                            },
                            "422": {"description": "Validation " "Error"},
                        },
                        "summary": "dummy route",
                    }
                }
            },
        }
        self.assertEqual(expected_schema, schema)

    def test_nested_param_get(self):
        @action(
            triggers=(WEB_GET,),
        )
        def dummy(node: Node) -> str:
            """dummy route"""

        action_ = get_action(dummy)
        action_endpoint = ActionEndpointFactory().create(action_, set(), [])
        schema = dict(paths={}, components={})
        action_endpoint.to_openapi_schema(schema)
        expected_schema = {
            "paths": {
                "/actions/dummy": {
                    "get": {
                        "responses": {
                            "422": {"description": "Validation Error"},
                            "200": {
                                "description": "Successful Response",
                                "content": {
                                    "application/json": {"schema": {"type": "string"}}
                                },
                            },
                        },
                        "operationId": "dummy",
                        "summary": "dummy route",
                        "parameters": [
                            {
                                "required": True,
                                "schema": {"type": "string"},
                                "name": "node.name",
                                "in": "query",
                            }
                        ],
                    }
                }
            },
            "components": {},
        }
        self.assertEqual(expected_schema, schema)


def build_request(
    method: str = "GET",
    server: str = "www.example.com",
    path: str = "/",
    query_string: str = None,
    headers: dict = None,
    body: str = None,
) -> Request:
    if headers is None:
        headers = {}
    receive = empty_receive
    if body:

        async def receive_body():
            return {"type": "http.request", "body": body.encode()}

        receive = receive_body

    request = Request(
        {
            "type": "http",
            "path": path,
            "headers": Headers(headers).raw,
            "http_version": "1.1",
            "method": method,
            "scheme": "https",
            "client": ("127.0.0.1", 8080),
            "server": (server, 443),
            "query_string": query_string,
        },
        receive=receive,
    )
    return request
