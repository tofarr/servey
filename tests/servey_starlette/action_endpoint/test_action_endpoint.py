import asyncio
import json
from datetime import datetime
from typing import List, Optional
from unittest import TestCase

from starlette.datastructures import Headers
from starlette.exceptions import HTTPException
from starlette.requests import Request, empty_receive

from servey.action.action import action, get_action
from servey.action.example import Example

# noinspection PyProtectedMember
from servey.servey_starlette.action_endpoint.action_endpoint import (
    _get_nullable_schema,
    _get_valid_openapi_param_schema,
)
from servey.servey_starlette.action_endpoint.factory.action_endpoint_factory import (
    ActionEndpointFactory,
)
from servey.trigger.web_trigger import WEB_GET, WEB_POST, WebTrigger, WebTriggerMethod
from tests.servey_strawberry.test_schema_factory import Node


class TestActionEndpoint(TestCase):
    def test_valid_input_get(self):
        @action(triggers=(WEB_GET,))
        def echo_get(val: str) -> str:
            return val

        action_endpoint = ActionEndpointFactory().create(
            get_action(echo_get), set(), []
        )
        # noinspection PyTypeChecker
        request = build_request(query_string=b"val=bar")
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(action_endpoint.execute(request))
        self.assertEqual(200, response.status_code)
        self.assertEqual("bar", json.loads(response.body))

    def test_valid_input_post(self):
        @action(triggers=(WEB_POST,))
        async def echo_get(val: str) -> str:
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
        # noinspection PyUnusedLocal
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
        # noinspection PyUnusedLocal
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
                                        "additionalProperties": True,
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
        # noinspection PyUnusedLocal
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

    def test_example_missing_parameters(self):
        # noinspection PyUnusedLocal
        @action(
            triggers=(WEB_GET,),
            examples=(
                Example("has_b", {"a": 1, "b": 2}, result=3),
                Example("missing_b", {"a": 1}, result=2),
            ),
        )
        def add(a: int, b: int = None) -> int:
            """Dummy"""

        endpoint = ActionEndpointFactory().create(get_action(add), set(), [])
        schema = {"paths": {}, "components": {}}
        endpoint.to_openapi_schema(schema)
        expected_schema = {
            "paths": {
                "/actions/add": {
                    "get": {
                        "responses": {
                            "422": {"description": "Validation Error"},
                            "200": {
                                "description": "Successful Response",
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "integer"},
                                        "examples": {
                                            "has_b": {"value": 3},
                                            "missing_b": {"value": 2},
                                        },
                                    }
                                },
                            },
                        },
                        "operationId": "add",
                        "summary": "Dummy",
                        "parameters": [
                            {
                                "required": True,
                                "schema": {"type": "integer"},
                                "name": "a",
                                "in": "query",
                                "examples": {
                                    "has_b": {"value": 1},
                                    "missing_b": {"value": 1},
                                },
                            },
                            {
                                "required": False,
                                "schema": {"type": "integer"},
                                "name": "b",
                                "in": "query",
                                "examples": {"has_b": {"value": 2}},
                            },
                        ],
                    }
                }
            },
            "components": {},
        }
        self.assertEqual(expected_schema, schema)

    def test_example_array_parameters(self):
        # noinspection PyUnusedLocal
        @action(
            triggers=(WEB_GET,),
            examples=(Example("standard", {"values": [1, 2, 3]}, result=6),),
        )
        def add(values: List[int]) -> int:
            """Dummy"""

        endpoint = ActionEndpointFactory().create(get_action(add), set(), [])
        schema = {"paths": {}, "components": {}}
        endpoint.to_openapi_schema(schema)
        expected_schema = {
            "paths": {
                "/actions/add": {
                    "get": {
                        "responses": {
                            "422": {"description": "Validation Error"},
                            "200": {
                                "description": "Successful Response",
                                "content": {
                                    "application/json": {
                                        "schema": {"type": "integer"},
                                        "examples": {
                                            "standard": {"value": 6},
                                        },
                                    }
                                },
                            },
                        },
                        "operationId": "add",
                        "summary": "Dummy",
                        "parameters": [
                            {
                                "required": True,
                                "schema": {
                                    "type": "array",
                                    "items": {"type": "integer"},
                                },
                                "name": "values",
                                "in": "query",
                                "examples": {"standard": {"value": [1, 2, 3]}},
                            }
                        ],
                    }
                }
            },
            "components": {},
        }
        self.assertEqual(expected_schema, schema)

    def test_example_array_object_parameters(self):
        # noinspection PyUnusedLocal
        @action(triggers=(WEB_GET,))
        def add(values: Optional[Node]) -> int:
            """Dummy"""

        endpoint = ActionEndpointFactory().create(get_action(add), set(), [])
        schema = {"paths": {}, "components": {}}
        endpoint.to_openapi_schema(schema)
        expected_schema = {
            "components": {},
            "paths": {
                "/actions/add": {
                    "get": {
                        "operationId": "add",
                        "parameters": [
                            {
                                "in": "query",
                                "name": "values.name",
                                "required": True,
                                "schema": {"type": "string"},
                            }
                        ],
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {"schema": {"type": "integer"}}
                                },
                                "description": "Successful " "Response",
                            },
                            "422": {"description": "Validation " "Error"},
                        },
                        "summary": "Dummy",
                    }
                }
            },
        }
        self.assertEqual(expected_schema, schema)

    def test_nullable_schema(self):
        self.assertIsNone(_get_nullable_schema({"anyOf": "invalid"}))
        self.assertIsNone(
            _get_nullable_schema(
                {
                    "anyOf": [
                        {"type": "string"},
                        {"type": "int"},
                    ]
                }
            )
        )

    def test_get_valid_openapi_param_schema(self):
        self.assertIsNone(_get_valid_openapi_param_schema({}))
        self.assertIsNone(_get_valid_openapi_param_schema({"type": "array"}))

    def test_get_with_path_params(self):
        # noinspection PyUnusedLocal
        @action(triggers=(WebTrigger(WebTriggerMethod.GET, "/find/{key}"),))
        def find(key: str) -> int:
            """Dummy"""
            return 17

        endpoint = ActionEndpointFactory().create(get_action(find), set(), [])
        schema = {"paths": {}, "components": {}}
        endpoint.to_openapi_schema(schema)
        expected_schema = {
            "components": {},
            "paths": {
                "/find/{key}": {
                    "get": {
                        "operationId": "find",
                        "parameters": [
                            {
                                "in": "path",
                                "name": "key",
                                "required": True,
                                "schema": {"type": "string"},
                            }
                        ],
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {"schema": {"type": "integer"}}
                                },
                                "description": "Successful " "Response",
                            },
                            "422": {"description": "Validation " "Error"},
                        },
                        "summary": "Dummy",
                    }
                }
            },
        }
        self.assertEqual(expected_schema, schema)
        request = build_request(path_params={"key": "bar"})
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(endpoint.execute(request))
        self.assertEqual(200, response.status_code)
        self.assertEqual(17, json.loads(response.body))

    def test_post_with_path_params(self):
        # noinspection PyUnusedLocal
        @action(triggers=(WebTrigger(WebTriggerMethod.POST, "/find/{key}"),))
        def find(key: str, value: str) -> int:
            """Dummy"""
            return len(key) + len(value)

        endpoint = ActionEndpointFactory().create(get_action(find), set(), [])
        schema = {"paths": {}, "components": {}}
        endpoint.to_openapi_schema(schema)
        expected_schema = {
            "components": {},
            "paths": {
                "/find/{key}": {
                    "post": {
                        "operationId": "find",
                        "parameters": [
                            {
                                "in": "path",
                                "name": "key",
                                "required": True,
                                "schema": {"type": "string"},
                            }
                        ],
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "additionalProperties": True,
                                        "properties": {"value": {"type": "string"}},
                                        "required": ["value"],
                                        "type": "object",
                                    }
                                }
                            },
                            "required": True,
                        },
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {"schema": {"type": "integer"}}
                                },
                                "description": "Successful " "Response",
                            },
                            "422": {"description": "Validation " "Error"},
                        },
                        "summary": "Dummy",
                    }
                }
            },
        }
        self.assertEqual(expected_schema, schema)
        request = build_request(
            method="POST",
            path_params={"key": "bar"},
            body=json.dumps({"value": "ping"}),
        )
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(endpoint.execute(request))
        self.assertEqual(200, response.status_code)
        self.assertEqual(7, json.loads(response.body))


def build_request(
    method: str = "GET",
    server: str = "www.example.com",
    path: str = "/",
    query_string: str = None,
    headers: dict = None,
    body: str = None,
    path_params: dict = None,
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
            "path_params": path_params,
        },
        receive=receive,
    )
    return request
