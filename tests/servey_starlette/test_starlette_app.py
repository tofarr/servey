from unittest import TestCase
from unittest.mock import patch
from uuid import UUID

from servey.action.action import action, get_action
from servey.trigger.web_trigger import WEB_GET


class TestStarletteApp(TestCase):

    def test_app(self):
        @action(triggers=(WEB_GET,))
        def dummy() -> UUID:
            """ No implementation required """

        with patch("servey.servey_starlette.route_factory.action_route_factory.find_actions", return_value=[get_action(dummy)]):
            from servey.servey_starlette.starlette_app import app
            self.assertGreater(len(app.routes), 4)
            next(r for r in app.routes if r.path == '/actions/dummy')

    def test_statics(self):
        from servey.servey_starlette import statics
        self.assertTrue(statics)
