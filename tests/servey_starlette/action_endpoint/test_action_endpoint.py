import asyncio
import json
from datetime import datetime
from unittest import TestCase

from starlette.datastructures import Headers
from starlette.exceptions import HTTPException
from starlette.requests import Request

from servey.action.action import action, get_action
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
        request = build_request(query_string="val=bar")
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
            """ dummy route """
        action_ = get_action(dummy)
        action_endpoint = ActionEndpointFactory().create(
            action_, set(), []
        )
        route = action_endpoint.get_route()
        self.assertEqual("dummy", route.name)
        self.assertEqual("/actions/dummy", route.path)
        self.assertEqual({'GET', 'HEAD'}, set(route.methods))

    def test_open_api_get(self):
        @action(triggers=(WEB_GET,))
        def dummy(id: str, value: float, count: int, flag: bool = True) -> datetime:
            """ dummy route """
        action_ = get_action(dummy)
        action_endpoint = ActionEndpointFactory().create(
            action_, set(), []
        )
        schema = dict(paths={}, components={})
        action_endpoint.to_openapi_schema(schema)
        expected_schema = {
          'paths': {
            '/actions/dummy': {
              'get': {
                'responses': {
                  '422': {
                    'description': 'Validation Error'
                  },
                  '200': {
                    'description': 'Successful Response',
                    'content': {
                      'application/json': {
                        'schema': {
                          'type': 'string',
                          'format': 'date-time'
                        }
                      }
                    }
                  }
                },
                'operationId': 'dummy',
                'summary': 'dummy route',
                'parameters': [
                  {
                    'required': True,
                    'schema': {
                      'type': 'string'
                    },
                    'name': 'id',
                    'in': 'query'
                  },
                  {
                    'required': True,
                    'schema': {
                      'type': 'number'
                    },
                    'name': 'value',
                    'in': 'query'
                  },
                  {
                    'required': True,
                    'schema': {
                      'type': 'integer'
                    },
                    'name': 'count',
                    'in': 'query'
                  },
                  {
                    'required': False,
                    'schema': {
                      'type': 'boolean'
                    },
                    'name': 'flag',
                    'in': 'query'
                  }
                ]
              }
            }
          },
          'components': {}
        }
        self.assertEqual(expected_schema, schema)

    def test_open_api_post(self):
        @action(triggers=(WEB_POST,))
        def dummy(node: Node) -> Node:
            """ dummy route """
        action_ = get_action(dummy)
        action_endpoint = ActionEndpointFactory().create(
            action_, set(), []
        )
        schema = dict(paths={}, components={})
        action_endpoint.to_openapi_schema(schema)
        expected_schema = {
          'paths': {
            '/actions/dummy': {
              'post': {
                'responses': {
                  '422': {
                    'description': 'Validation Error'
                  },
                  '200': {
                    'description': 'Successful Response',
                    'content': {
                      'application/json': {
                        'schema': {
                          '$ref': '#/components/Node'
                        }
                      }
                    }
                  }
                },
                'operationId': 'dummy',
                'summary': 'dummy route',
                'requestBody': {
                  'content': {
                    'application/json': {
                      'schema': {
                          'type': 'object',
                          'properties': {
                              'node': {
                                  '$ref': '#/components/Node'
                              }
                          },
                          'additionalProperties': False,
                          'required': [
                              'node'
                          ]
                      }
                    }
                  },
                  'required': True
                }
              }
            }
          },
          'components': {
            'Node': {
              'type': 'object',
              'name': 'Node',
              'properties': {
                'name': {
                  'type': 'string'
                },
                'child_nodes': {
                  'type': 'array',
                  'items': {
                    '$ref': '#/components/Node'
                  }
                }
              },
              'additionalProperties': False,
              'required': [
                'name'
              ],
              'description': "Node(name: str, child_nodes: List[ForwardRef('tests.servey_strawberry.test_schema_factory.Node')] = <factory>)"
            }
          }
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
        }
    )
    if body:

        async def request_body():
            return body

        request.body = request_body
    return request
