from dataclasses import dataclass
from unittest import TestCase
from unittest.mock import patch

from servey.action.action import action, get_action
from servey.errors import ServeyError
from servey.servey_aws.lambda_router import invoke
from servey.servey_aws.router.appsync_router import AppsyncRouter
from servey.trigger.web_trigger import WEB_GET


class TestLambdaInvoker(TestCase):
    def test_router(self):
        @action(triggers=WEB_GET)
        def echo_get(val: str) -> str:
            return val

        with patch(
            "servey.servey_aws.router.router.find_actions",
            return_value=[get_action(echo_get)],
        ):
            event = dict(action_name="echo_get", params=dict(val="foo"))
            result = invoke(event, None)
            expected_result = "foo"
            self.assertEqual(expected_result, result)

    def test_router_no_handler(self):
        @action(triggers=WEB_GET)
        def echo_get(val: str) -> str:
            """Dummy"""

        with patch(
            "servey.servey_aws.router.router.find_actions",
            return_value=[get_action(echo_get)],
        ), self.assertRaises(StopIteration):
            event = dict(action_name="not_existing")
            invoke(event, None)

    def test_router_no_action(self):
        @action(triggers=WEB_GET)
        def echo_get(val: str) -> str:
            """Dummy"""

        with patch(
            "servey.servey_aws.router.router.find_actions",
            return_value=[get_action(echo_get)],
        ), self.assertRaises(ServeyError):
            invoke({}, None)

    def test_router_api_gateway(self):
        @action(triggers=WEB_GET)
        def echo_get(val: str) -> str:
            return val

        with patch(
            "servey.servey_aws.router.router.find_actions",
            return_value=[get_action(echo_get)],
        ), patch(
            "servey.finder.action_finder_abc.find_actions",
            return_value=[get_action(echo_get)],
        ):
            event = dict(path="/actions/echo-get", params=dict(val="foo"))
            result = invoke(event, None)
            expected_result = "foo"
            self.assertEqual(expected_result, result)

    def test_router_appsync(self):
        @action(triggers=WEB_GET)
        def echo_get(val: str) -> str:
            return val

        with patch(
            "servey.servey_aws.router.router.find_actions",
            return_value=[get_action(echo_get)],
        ), patch(
            "servey.finder.action_finder_abc.find_actions",
            return_value=[get_action(echo_get)],
        ):
            event = dict(path="/actions/echo-get", params=dict(val="foo"))
            result = invoke(event, None)
            expected_result = "foo"
            self.assertEqual(expected_result, result)

    def test_nested_router_appsync(self):

        @dataclass
        class NumberStats:
            int_value: int

            @action
            def factorial(self) -> int:
                result_ = 1
                value = self.int_value
                while value > 1:
                    result_ *= value
                    value -= 1
                return result_

        @action(triggers=WEB_GET)
        def number_stats(int_value: int) -> NumberStats:
            return NumberStats(int_value)

        event = {
            "arguments": {},
            "identity": None,
            "source": {
                "intValue": 5,
            },
            "prev": None,
            "info": {
                "selectionSetList": [],
                "selectionSetGraphQL": "{}",
                "fieldName": "factorial",
                "parentTypeName": "NumberStats",
                "variables": {
                    "pageKey": None
                }
            },
            "stash": {}
        }
        action_ = get_action(number_stats)
        router = AppsyncRouter()
        setattr(router, '_web_trigger_actions', ((action_, action_.triggers[0]),))
        handler = router.create_handler(event, None)
        result = handler.handle(event, None)
        self.assertEqual(120, result)
