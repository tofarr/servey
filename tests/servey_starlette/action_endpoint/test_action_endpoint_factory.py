from unittest import TestCase

from servey.action.action import action, get_action
from servey.errors import ServeyError
from servey.servey_starlette.action_endpoint.factory.action_endpoint_factory import (
    ActionEndpointFactory,
)
from servey.trigger.web_trigger import WebTrigger, WebTriggerMethod, WEB_POST


class TestActionEndpointFactory(TestCase):
    def test_multi_paths(self):
        # noinspection PyTypeChecker
        @action(
            triggers=(
                WebTrigger(WebTriggerMethod.POST, "/foo"),
                WebTrigger(WebTriggerMethod.POST, "/bar"),
            )
        )
        def dummy() -> int:
            """No action required"""

        factory = ActionEndpointFactory()
        with self.assertRaises(ServeyError):
            factory.create(get_action(dummy), set(), [])

    def test_custom_path(self):
        # noinspection PyTypeChecker
        @action(triggers=(WebTrigger(WebTriggerMethod.GET, "/foo"),))
        def dummy() -> int:
            """No action required"""

        factory = ActionEndpointFactory()
        endpoint = factory.create(get_action(dummy), set(), [])
        route = endpoint.get_route()
        # noinspection PyTypeChecker
        self.assertEqual("/foo", route.path)

    def test_invalid_return(self):
        # noinspection PyTypeChecker
        @action(triggers=(WEB_POST,))
        def dummy():
            """No action required"""

        factory = ActionEndpointFactory()
        with self.assertRaises(ServeyError):
            factory.create(get_action(dummy), set(), [])
