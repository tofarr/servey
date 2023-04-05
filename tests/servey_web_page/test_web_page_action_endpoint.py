from asyncio import get_event_loop
from http.client import HTTPException
from unittest import TestCase
from unittest.mock import patch

from jinja2 import Environment, PackageLoader

from servey.action.action import action, get_action
from servey.errors import ServeyError
from servey.servey_web_page.redirect import Redirect
from servey.servey_web_page.web_page_action_endpoint_factory import (
    WebPageActionEndpointFactory,
)
from servey.servey_web_page.web_page_trigger import WebPageTrigger
from servey.trigger.web_trigger import WebTriggerMethod
from tests.servey_starlette.action_endpoint.test_action_endpoint import build_request


class TestWebPageActionEndpoint(TestCase):
    def test_endpoint(self):
        @action(triggers=WebPageTrigger())
        def add(a: int, b: int) -> int:
            return a + b

        with patch(
            "servey.servey_web_page.web_page_action_endpoint.get_environment",
            return_value=Environment(
                loader=PackageLoader("tests.servey_web_page", "templates"),
                auto_reload=False,  # Uvicorn handles this
            ),
        ):
            factory = WebPageActionEndpointFactory()
            endpoint = factory.create(get_action(add), set(), [factory])
            self.assertEqual("add.j2", endpoint.template_name)
            schema = {}
            endpoint.to_openapi_schema(schema)
            self.assertEqual({}, schema)
            request = build_request(path="/add", query_string="a=3&b=5")
            loop = get_event_loop()
            result = loop.run_until_complete(endpoint.execute(request))
            self.assertEqual(b"The result was 8", result.body)

    def test_redirect(self):
        @action(triggers=WebPageTrigger())
        def add(a: int, b: int) -> Redirect:
            return Redirect(f"https://foobar.com/{a+b}")

        with patch(
            "servey.servey_web_page.web_page_action_endpoint.get_environment",
            return_value=Environment(
                loader=PackageLoader("tests.servey_web_page", "templates"),
                auto_reload=False,  # Uvicorn handles this
            ),
        ):
            factory = WebPageActionEndpointFactory()
            endpoint = factory.create(get_action(add), set(), [factory])
            request = build_request(path="/add", query_string="a=3&b=5")
            loop = get_event_loop()
            result = loop.run_until_complete(endpoint.execute(request))
            self.assertEqual(b"", result.body)
            self.assertEqual("https://foobar.com/8", result.headers["location"])

    def test_error(self):
        @action(triggers=WebPageTrigger())
        def add(a: int, b: int) -> int:
            return str(a + b)

        with patch(
            "servey.servey_web_page.web_page_action_endpoint.get_environment",
            return_value=Environment(
                loader=PackageLoader("tests.servey_web_page", "templates"),
                auto_reload=False,  # Uvicorn handles this
            ),
        ):
            factory = WebPageActionEndpointFactory()
            endpoint = factory.create(get_action(add), set(), [factory])
            request = build_request(path="/add", query_string="a=3&b=5")
            with self.assertRaises(HTTPException):
                loop = get_event_loop()
                loop.run_until_complete(endpoint.execute(request))

    def test_no_triggers(self):
        @action
        def add(a: int, b: int) -> int:
            return str(a + b)

        factory = WebPageActionEndpointFactory()
        result = factory.create(get_action(add), set(), [factory])
        self.assertIsNone(result)

    def test_multi_triggers(self):
        @action(
            triggers=(
                WebPageTrigger(WebTriggerMethod.GET),
                WebPageTrigger(WebTriggerMethod.POST),
            )
        )
        def add(a: int, b: int) -> int:
            return str(a + b)

        factory = WebPageActionEndpointFactory()
        with self.assertRaises(ServeyError):
            factory.create(get_action(add), set(), [factory])

    def test_no_result(self):
        @action(triggers=WebPageTrigger(WebTriggerMethod.GET))
        def dummy():
            pass

        with patch(
            "servey.servey_web_page.web_page_action_endpoint.get_environment",
            return_value=Environment(
                loader=PackageLoader("tests.servey_web_page", "templates"),
                auto_reload=False,  # Uvicorn handles this
            ),
        ):
            factory = WebPageActionEndpointFactory()
            endpoint = factory.create(get_action(dummy), set(), [factory])
            request = build_request(path="/dummy", query_string="a=3&b=5")

            loop = get_event_loop()
            result = loop.run_until_complete(endpoint.execute(request))
            self.assertEqual(b"No model was passed in here", result.body)
