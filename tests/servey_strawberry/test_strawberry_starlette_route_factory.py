import os
from unittest import TestCase
from unittest.mock import patch

from servey.servey_strawberry.strawberry_starlette_route_factory import (
    StrawberryStarletteRouteFactory,
)


class TestStrawberryStarletteRouteFactory(TestCase):
    def test_create_routes(self):
        with patch.dict(
            os.environ,
            {"SERVEY_MAIN": "tests.servey_strawberry"},
        ):
            factory = StrawberryStarletteRouteFactory()
            routes = list(factory.create_routes())
            self.assertEqual(3, len(routes))

    def test_no_debug(self):
        with patch.dict(
            os.environ,
            {
                "SERVEY_MAIN": "tests.servey_strawberry",
                "SERVER_DEBUG": "0",
            },
        ):
            factory = StrawberryStarletteRouteFactory()
            routes = list(factory.create_routes())
            self.assertEqual(2, len(routes))

    def test_create_no_routes(self):
        with patch("servey.finder.action_finder_abc.find_actions", return_value=[]):
            factory = StrawberryStarletteRouteFactory()
            routes = list(factory.create_routes())
            self.assertEqual([], routes)

    def test_create_routes_no_module(self):
        def raise_module_not_found():
            raise ModuleNotFoundError()

        factory = StrawberryStarletteRouteFactory()
        with patch(
            "servey.servey_strawberry.schema_factory.create_schema",
            raise_module_not_found,
        ):
            routes = list(factory.create_routes())
            self.assertEqual([], routes)
