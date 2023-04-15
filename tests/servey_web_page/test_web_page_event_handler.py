from unittest import TestCase
from unittest.mock import patch

from servey.action.action import action, get_action
from servey.servey_web_page.redirect import Redirect
from servey.servey_web_page.web_page_event_handler import WebPageEventHandlerFactory
from servey.servey_web_page.web_page_trigger import WebPageTrigger


class TestWebPageEventHandler(TestCase):
    def test_event_handler(self):
        @action(triggers=WebPageTrigger())
        def add(a: int, b: int) -> int:
            return a + b

        with patch(
            "servey.servey_web_page.web_page_trigger.get_servey_main",
            return_value="tests.servey_web_page",
        ):
            factory = WebPageEventHandlerFactory()
            handler = factory.create(get_action(add))
            event = {"httpMethod": "GET", "queryStringParameters": {"a": "3", "b": "5"}}
            context = {}
            self.assertTrue(handler.is_usable(event, context))
            result = handler.handle(event, context)
            expected = {
                "statusCode": 200,
                "headers": {"Content-Type": "text/html"},
                "body": "The result was 8",
            }
            self.assertEqual(expected, result)

    def test_async(self):
        @action(triggers=WebPageTrigger())
        async def add(a: int, b: int) -> int:
            return a + b

        with patch(
            "servey.servey_web_page.web_page_trigger.get_servey_main",
            return_value="tests.servey_web_page",
        ):
            factory = WebPageEventHandlerFactory()
            handler = factory.create(get_action(add))
            event = {"httpMethod": "GET", "queryStringParameters": {"a": "3", "b": "5"}}
            context = {}
            self.assertTrue(handler.is_usable(event, context))
            result = handler.handle(event, context)
            expected = {
                "statusCode": 200,
                "headers": {"Content-Type": "text/html"},
                "body": "The result was 8",
            }
            self.assertEqual(expected, result)

    def test_redirect(self):
        @action(triggers=WebPageTrigger())
        def add(a: int, b: int) -> Redirect:
            return Redirect(f"https://foobar.com/{a+b}")

        factory = WebPageEventHandlerFactory()
        handler = factory.create(get_action(add))
        event = {"httpMethod": "GET", "queryStringParameters": {"a": "3", "b": "5"}}
        context = {}
        self.assertTrue(handler.is_usable(event, context))
        result = handler.handle(event, context)
        expected = {"statusCode": 307, "headers": {"Location": "https://foobar.com/8"}}
        self.assertEqual(expected, result)
