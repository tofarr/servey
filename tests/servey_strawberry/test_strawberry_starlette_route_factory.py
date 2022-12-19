import os
from datetime import datetime
from unittest import TestCase
from unittest.mock import patch

from servey.action.action import action
from servey.servey_strawberry.strawberry_starlette_route_factory import (
    StrawberryStarletteRouteFactory,
)
from servey.trigger.web_trigger import WEB_GET


class TestStrawberryStarletteRouteFactory(TestCase):
    def test_create_routes(self):
        with patch.dict(
            os.environ,
            {
                "SERVEY_ACTION_PATH": "tests.servey_strawberry.test_strawberry_starlette_route_factory"
            },
        ):
            factory = StrawberryStarletteRouteFactory()
            routes = list(factory.create_routes())
            self.assertEqual(3, len(routes))

    def test_no_debug(self):
        with patch.dict(
            os.environ,
            {
                "SERVEY_ACTION_PATH": "tests.servey_strawberry.test_strawberry_starlette_route_factory",
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


@action(triggers=(WEB_GET,))
def get_the_time() -> datetime:
    """This is a dummy"""