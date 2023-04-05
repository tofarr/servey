from unittest import TestCase
from unittest.mock import patch, MagicMock

from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from servey.servey_starlette.route_factory.static_site_route_factory import (
    StaticSiteRouteFactory,
)


class TestStaticSiteRouteFactory(TestCase):
    def test_create_routes(self):
        mock_directory = MagicMock()
        mock_directory.exists.return_value = True
        mock_directory.isdir.return_value = True
        route_factory = StaticSiteRouteFactory(path="/foobar", directory=mock_directory)

        with patch("os.path", mock_directory):
            routes = list(route_factory.create_routes())
            expected_routes = [
                Mount(
                    path="/foobar",
                    app=StaticFiles(directory=mock_directory, html=True),
                    name="static_site",
                )
            ]
            self.assertEqual(1, len(routes))
            self.assertEqual("/foobar", routes[0].path)
            self.assertEqual("static_site", routes[0].name)
