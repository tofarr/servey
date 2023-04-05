from unittest import TestCase

from servey.action.action import action, get_action
from servey.servey_web_page.web_page_trigger import WebPageTrigger
from servey.servey_web_page.web_page_trigger_handler import WebPageTriggerHandler


class TestWebPageTriggerHandler(TestCase):
    def test_event_handler(self):
        @action(triggers=WebPageTrigger())
        def add(a: int, b: int) -> int:
            return a + b

        lambda_definition = {}
        handler = WebPageTriggerHandler()
        action_ = get_action(add)
        handler.handle_trigger(action_, action_.triggers[0], lambda_definition)
        expected = {
            "events": [{"http": {"cors": True, "method": "get", "path": "/add"}}]
        }
        self.assertEqual(expected, lambda_definition)
