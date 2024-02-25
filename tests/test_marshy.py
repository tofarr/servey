from unittest import TestCase
from unittest.mock import patch

from injecty import InjectyContext

from injecty_config_servey import (
    configure_starlette,
    configure_strawberry,
    configure_strawberry_starlette,
    configure_aws,
    configure_serverless,
    configure_celery,
    configure_jinja2,
    configure_web_page_action_endpoint_factory,
    configure_web_page_event_handler,
    configure_web_page_trigger_handler,
)


class TestMarshy(TestCase):
    def test_configure_starlette(self):
        with patch(
            "injecty.injecty_context.InjectyContext.register_impl", _mock_register_impl
        ):
            with self.assertRaises(ModuleNotFoundError):
                configure_starlette(InjectyContext())

    def test_configure_strawberry(self):
        with patch(
            "injecty.injecty_context.InjectyContext.register_impl", _mock_register_impl
        ):
            with self.assertRaises(ModuleNotFoundError):
                configure_strawberry(InjectyContext())

    def test_configure_strawberry_starlette(self):
        with patch(
            "injecty.injecty_context.InjectyContext.register_impl", _mock_register_impl
        ):
            with self.assertRaises(ModuleNotFoundError):
                configure_strawberry_starlette(InjectyContext())

    def test_configure_aws(self):
        with patch(
            "injecty.injecty_context.InjectyContext.register_impl", _mock_register_impl
        ):
            with self.assertRaises(ModuleNotFoundError):
                configure_aws(InjectyContext())

    def test_configure_serverless(self):
        with patch(
            "injecty.injecty_context.InjectyContext.register_impl", _mock_register_impl
        ):
            with self.assertRaises(ModuleNotFoundError):
                configure_serverless(InjectyContext())

    def test_configure_celery(self):
        with patch(
            "injecty.injecty_context.InjectyContext.register_impl", _mock_register_impl
        ):
            with self.assertRaises(ModuleNotFoundError):
                configure_celery(InjectyContext())

    def test_configure_jinja2(self):
        with patch(
            "injecty.injecty_context.InjectyContext.register_impl", _mock_register_impl
        ):
            with self.assertRaises(ModuleNotFoundError):
                configure_jinja2(InjectyContext())

    def test_configure_web_page_action_endpoint_factory(self):
        with patch(
            "injecty.injecty_context.InjectyContext.register_impl", _mock_register_impl
        ):
            with self.assertRaises(ModuleNotFoundError):
                configure_web_page_action_endpoint_factory(InjectyContext())

    def test_configure_web_page_event_handler(self):
        with patch(
            "injecty.injecty_context.InjectyContext.register_impl", _mock_register_impl
        ):
            with self.assertRaises(ModuleNotFoundError):
                configure_web_page_event_handler(InjectyContext())

    def test_configure_web_page_trigger_handler(self):
        with patch(
            "injecty.injecty_context.InjectyContext.register_impl", _mock_register_impl
        ):
            with self.assertRaises(ModuleNotFoundError):
                configure_web_page_trigger_handler(InjectyContext())


def _mock_register_impl(self, base, impl, check_type: bool = True):
    raise ModuleNotFoundError()
