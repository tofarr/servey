import asyncio
import json
from datetime import datetime, timezone
from unittest import TestCase
from email.utils import parsedate

from servey.action.action import action
from servey.cache_control.ttl_cache_control import TtlCacheControl
from servey.servey_starlette.action_endpoint.caching_action_endpoint import CachingActionEndpoint
from servey.servey_starlette.action_endpoint.factory.action_endpoint_factory import ActionEndpointFactory
from servey.trigger.web_trigger import WEB_GET
from tests.servey_starlette.action_endpoint.test_action_endpoint import build_request


class TestCachingActionEndpoint(TestCase):

    def test_caching_input_get(self):
        @action(triggers=(WEB_GET,), cache_control=TtlCacheControl(30))
        def echo_get(val: str) -> str:
            return val

        action_endpoint = CachingActionEndpoint(ActionEndpointFactory().create(echo_get.__servey_action__, set(), []))
        request = build_request(query_string='val=bar')
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(action_endpoint.execute(request))
        loop.close()
        self.assertEqual(200, response.status_code)
        self.assertEqual('bar', json.loads(response.body))
        self.assertEqual('TCk/8BCnMPCXJ2EzHRtWeEeNQlwtxc79FtjyAFnkl/M=', response.headers['etag'])
        self.assertEqual('private,max-age=29', response.headers['cache-control'])
        expected_expires = int(datetime.now().timestamp()) + 30
        expires = int(datetime(*(parsedate(response.headers['expires'])[:6]), tzinfo=timezone.utc).timestamp())
        self.assertAlmostEqual(expected_expires, expires, 1)
