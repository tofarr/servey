import asyncio
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Any
from unittest import TestCase
from email.utils import parsedate

from starlette.requests import Request
from starlette.responses import Response

from servey.action.action import action, Action, get_action
from servey.cache_control.timestamp_cache_control import TimestampCacheControl
from servey.cache_control.ttl_cache_control import TtlCacheControl
from servey.servey_starlette.action_endpoint.caching_action_endpoint import (
    CachingActionEndpoint,
)
from servey.servey_starlette.action_endpoint.factory.action_endpoint_factory import (
    ActionEndpointFactory,
)
from servey.trigger.web_trigger import WEB_GET
from tests.servey_starlette.action_endpoint.test_action_endpoint import build_request


class TestCachingActionEndpoint(TestCase):
    def test_caching_input_get(self):
        @action(triggers=(WEB_GET,), cache_control=TtlCacheControl(30))
        def echo_get(val: str) -> str:
            return val

        action_endpoint = CachingActionEndpoint(
            ActionEndpointFactory().create(echo_get.__servey_action__, set(), [])
        )
        request = build_request(query_string="val=bar")
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(action_endpoint.execute(request))

        self.assertEqual(200, response.status_code)
        self.assertEqual("bar", json.loads(response.body))
        # noinspection SpellCheckingInspection
        self.assertEqual(
            "TCk/8BCnMPCXJ2EzHRtWeEeNQlwtxc79FtjyAFnkl/M=", response.headers["etag"]
        )
        self.assertEqual("private,max-age=29", response.headers["cache-control"])
        expected_expires = int(datetime.now().timestamp()) + 30
        expires = int(
            datetime(
                *(parsedate(response.headers["expires"])[:6]), tzinfo=timezone.utc
            ).timestamp()
        )
        self.assertAlmostEqual(expected_expires, expires, 1)

        # noinspection SpellCheckingInspection
        request = build_request(
            query_string="val=bar",
            headers={"If-Match": "TCk/8BCnMPCXJ2EzHRtWeEeNQlwtxc79FtjyAFnkl/M="},
        )
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(action_endpoint.execute(request))

        self.assertEqual(304, response.status_code)
        self.assertEqual(b"", response.body)

    def test_execute_with_context_500(self):
        expected_response = Response(b"", 500)
        # noinspection PyTypeChecker
        endpoint = CachingActionEndpoint(MockActionEndpoint(None, expected_response))
        loop = asyncio.get_event_loop()
        request = build_request()
        response = loop.run_until_complete(endpoint.execute_with_context(request, {}))
        self.assertEqual(500, response.status_code)
        self.assertEqual(b"", response.body)

    def test_execute_with_context_last_modified(self):
        expected_response = Response(
            json.dumps({"updated_at": "2022-01-01 00:00:00+00:00"}),
            200,
            {"Last-Modified": "Sat, 1 Jan 2022 00:00:00 GMT"},
        )
        # noinspection PyTypeChecker
        action_ = Action(None, "foobar", cache_control=TimestampCacheControl())
        # noinspection PyTypeChecker
        endpoint = CachingActionEndpoint(MockActionEndpoint(action_, expected_response))
        loop = asyncio.get_event_loop()
        request = build_request(
            headers={"If-Modified-Since": "Sun, 1 Feb 2022 00:00:00 GMT"}
        )
        response = loop.run_until_complete(endpoint.execute_with_context(request, {}))
        self.assertEqual(304, response.status_code)
        self.assertEqual(b"", response.body)

    def test_to_openapi_schema(self):
        # noinspection PyUnusedLocal
        @action(triggers=(WEB_GET,))
        def dummy_lookup(id: str) -> str:
            """No action required"""

        caching_action_endpoint = CachingActionEndpoint(
            action_endpoint=ActionEndpointFactory().create(
                get_action(dummy_lookup), set(), []
            )
        )
        schema = dict(paths={}, components={})
        caching_action_endpoint.to_openapi_schema(schema)
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
                }
            },
            "paths": {
                "/actions/dummy-lookup": {
                    "get": {
                        "operationId": "dummy_lookup",
                        "parameters": [
                            {
                                "in": "query",
                                "name": "id",
                                "required": True,
                                "schema": {"type": "string"},
                            }
                        ],
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {"schema": {"type": "string"}}
                                },
                                "description": "Successful Response",
                            },
                            "304": {"content": {}, "description": "not_modified"},
                            "422": {"description": "Validation " "Error"},
                        },
                        "summary": "No action required",
                    }
                }
            },
        }
        self.assertEqual(expected_schema, schema)


@dataclass
class MockActionEndpoint:
    action: Action
    response: Response

    def get_action(self) -> Action:
        return self.action

    # noinspection PyUnusedLocal
    async def execute_with_context(
        self, request: Request, context: Dict[str, Any]
    ) -> Response:
        return self.response
