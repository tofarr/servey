from unittest import TestCase

from servey.servey_starlette.middleware.cors_middleware_factory import (
    CORSMiddlewareFactory,
)


class TestCorsMiddlewareFactory(TestCase):
    def test_create(self):
        middleware = CORSMiddlewareFactory(allow_origins=["foo.com", "bar.com"])
        self.assertIsNotNone(middleware.create())
