import os
from unittest import TestCase
from unittest.mock import patch
from uuid import UUID

from servey.action.action import action, get_action
from servey.trigger.fixed_rate_trigger import FixedRateTrigger


class TestStarletteApp(TestCase):
    def test_app(self):
        @action(triggers=(FixedRateTrigger(10),))
        def ping() -> UUID:
            """No implementation required"""

        with (
            patch(
                "servey.servey_starlette.route_factory.action_route_factory.find_actions",
                return_value=[get_action(ping)],
            ),
            patch.dict(os.environ, dict(CELERY_BROKER="redis://localhost:6379/0")),
        ):
            from servey.servey_celery.celery_app import app

            self.assertTrue(app.tasks.get("actions.ping"))
