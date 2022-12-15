import asyncio
import json
from unittest import TestCase

from starlette.datastructures import Headers
from starlette.exceptions import HTTPException
from starlette.requests import Request

from servey.action.action import action
from servey.servey_starlette.action_endpoint.factory.action_endpoint_factory import ActionEndpointFactory
from servey.trigger.web_trigger import WEB_GET, WEB_POST


class TestActionEndpoint(TestCase):

    def test_valid_input_get(self):
        @action(triggers=(WEB_GET,))
        def echo_get(val: str) -> str:
            return val

        action_endpoint = ActionEndpointFactory().create(echo_get.__servey_action__, set(), [])
        request = build_request(query_string='val=bar')
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(action_endpoint.execute(request))
        loop.close()
        self.assertEqual(200, response.status_code)
        self.assertEqual('bar', json.loads(response.body))

    def test_valid_input_post(self):
        @action(triggers=(WEB_POST,))
        def echo_get(val: str) -> str:
            return val

        action_endpoint = ActionEndpointFactory().create(echo_get.__servey_action__, set(), [])
        request = build_request(method='POST', body=json.dumps(dict(val='bar')))
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(action_endpoint.execute(request))
        loop.close()
        self.assertEqual(200, response.status_code)
        self.assertEqual('bar', json.loads(response.body))

    def test_invalid_input(self):
        @action(triggers=(WEB_GET,))
        def echo_get(val: int) -> int:
            return val

        action_endpoint = ActionEndpointFactory().create(echo_get.__servey_action__, set(), [])
        request = build_request(query_string='val=bar')
        loop = asyncio.get_event_loop()
        with self.assertRaises(HTTPException):
            loop.run_until_complete(action_endpoint.execute(request))
        loop.close()

    def test_invalid_output(self):
        @action(triggers=(WEB_GET,))
        def echo_get() -> int:
            return "foobar"

        action_endpoint = ActionEndpointFactory().create(echo_get.__servey_action__, set(), [])
        request = build_request()
        loop = asyncio.get_event_loop()
        with self.assertRaises(HTTPException):
            loop.run_until_complete(action_endpoint.execute(request))
        action_endpoint.result_schema = None
        loop.run_until_complete(action_endpoint.execute(request))
        loop.close()


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
            "query_string": query_string
        }
    )
    if body:
        async def request_body():
            return body

        request.body = request_body
    return request