import json
import os
from unittest import TestCase
from unittest.mock import patch

from marshy.marshaller import NoOpMarshaller
from schemey import schema_from_type

from servey.servey_starlette.route_factory.asyncapi_route_factory import (
    AsyncapiRouteFactory,
)
from servey.subscription.subscription import Subscription
from tests.servey_starlette.action_endpoint.test_action_endpoint import build_request


class TestAsyncapiRouteFactory(TestCase):
    def test_endpoint(self):
        with (
            patch(
                "servey.servey_starlette.route_factory.asyncapi_route_factory.find_subscriptions",
                return_value=[
                    Subscription(
                        "my_message", NoOpMarshaller(str), schema_from_type(str)
                    ),
                ],
            ),
            patch.dict(os.environ, {"SERVER_WS_URL": "https://foo.com/"}),
        ):
            route = AsyncapiRouteFactory()
            response = route.endpoint(build_request())
            result = json.loads(response.body)
            expected_result = {
                "asyncapi": "2.5.0",
                "info": {"title": "Servey", "version": "0.1.0"},
                "channels": {
                    "/subscription": {
                        "publish": {
                            "message": {
                                "payload": {
                                    "properties": {
                                        "type": {"enum": ["Subscribe", "Unsubscribe"]},
                                        "payload": {"type": "string"},
                                    },
                                    "additionalProperties": False,
                                }
                            }
                        },
                        "subscribe": {
                            "message": {
                                "payload": {
                                    "anyOf": [
                                        {
                                            "properties": {
                                                "type": {"const": "type"},
                                                "payload": {"type": "string"},
                                            },
                                            "additionalProperties": False,
                                            "required": ["type", "payload"],
                                        }
                                    ]
                                }
                            }
                        },
                    }
                },
                "components": {},
                "servers": {
                    "production": {"url": "https://foo.com/", "protocol": "wss"}
                },
            }
            self.assertEqual(expected_result, result)
