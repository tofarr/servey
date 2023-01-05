from datetime import datetime
from unittest import TestCase
from unittest.mock import patch
from uuid import UUID

from servey.action.action import action, get_action
from servey.cache_control.ttl_cache_control import TtlCacheControl
from servey.security.access_control.scope_access_control import ScopeAccessControl
from servey.security.authorization import Authorization
from servey.trigger.web_trigger import WEB_GET


class TestStarletteApp(TestCase):
    def test_app(self):
        @action(triggers=(WEB_GET,))
        def dummy() -> UUID:
            """No implementation required"""

        # noinspection PyUnusedLocal
        @action(triggers=(WEB_GET,), access_control=ScopeAccessControl("root"))
        def secured_action(auth: Authorization) -> str:
            """ No implementation required """ ""

        @action(triggers=(WEB_GET,), cache_control=TtlCacheControl(30))
        def cached_action() -> datetime:
            """ No implementation required """ ""

        with patch(
            "servey.servey_starlette.route_factory.action_route_factory.find_actions",
            return_value=[
                get_action(dummy),
                get_action(secured_action),
                get_action(cached_action),
            ],
        ):
            from servey.servey_starlette.starlette_app import app

            self.assertEqual(len(app.routes), 11)
            next(r for r in app.routes if r.path == "/actions/dummy")
            next(r for r in app.routes if r.path == "/actions/secured-action")
            next(r for r in app.routes if r.path == "/actions/cached-action")

    def test_statics(self):
        from servey.servey_starlette import statics

        self.assertTrue(statics)
