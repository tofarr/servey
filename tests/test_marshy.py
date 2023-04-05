from unittest import TestCase
from unittest.mock import patch

from marshy.marshaller_context import MarshallerContext

from marshy_config_servey import (
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
        with patch("marshy_config_servey.register_impl", _mock_register_impl):
            with self.assertRaises(ModuleNotFoundError):
                configure_starlette(MarshallerContext())

    def test_configure_strawberry(self):
        with patch("marshy_config_servey.register_impl", _mock_register_impl):
            with self.assertRaises(ModuleNotFoundError):
                configure_strawberry(MarshallerContext())

    def test_configure_strawberry_starlette(self):
        with patch("marshy_config_servey.register_impl", _mock_register_impl):
            with self.assertRaises(ModuleNotFoundError):
                configure_strawberry_starlette(MarshallerContext())

    def test_configure_aws(self):
        with patch("marshy_config_servey.register_impl", _mock_register_impl):
            with self.assertRaises(ModuleNotFoundError):
                configure_aws(MarshallerContext())

    def test_configure_serverless(self):
        with patch("marshy_config_servey.register_impl", _mock_register_impl):
            with self.assertRaises(ModuleNotFoundError):
                configure_serverless(MarshallerContext())

    def test_configure_celery(self):
        with patch("marshy_config_servey.register_impl", _mock_register_impl):
            with self.assertRaises(ModuleNotFoundError):
                configure_celery(MarshallerContext())

    def test_configure_jinja2(self):
        with patch("marshy_config_servey.register_impl", _mock_register_impl):
            with self.assertRaises(ModuleNotFoundError):
                configure_jinja2(MarshallerContext())

    def test_configure_web_page_action_endpoint_factory(self):
        with patch("marshy_config_servey.register_impl", _mock_register_impl):
            with self.assertRaises(ModuleNotFoundError):
                configure_web_page_action_endpoint_factory(MarshallerContext())

    def test_configure_web_page_event_handler(self):
        with patch("marshy_config_servey.register_impl", _mock_register_impl):
            with self.assertRaises(ModuleNotFoundError):
                configure_web_page_event_handler(MarshallerContext())

    def test_configure_web_page_trigger_handler(self):
        with patch("marshy_config_servey.register_impl", _mock_register_impl):
            with self.assertRaises(ModuleNotFoundError):
                configure_web_page_trigger_handler(MarshallerContext())


def _mock_register_impl(base, impl, context=None):
    raise ModuleNotFoundError()
