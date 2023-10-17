import importlib
import os
from unittest import TestCase
from unittest.mock import patch
from uuid import UUID

from servey.action.action import action, get_action
from servey.event_channel.background.background_action_channel import (
    background_action_channel,
)
from servey.servey_celery.celery_config.fixed_rate_trigger_config import (
    FixedRateTriggerConfig,
)
from servey.trigger.fixed_rate_trigger import FixedRateTrigger


class TestCeleryApp(TestCase):
    def test_app(self):
        @action(triggers=(FixedRateTrigger(10),))
        def ping() -> UUID:
            """No implementation required"""

        # noinspection PyUnusedLocal
        @action
        def consume_message(message: str):
            """No implementation required"""

        channel = background_action_channel(consume_message)

        with (
            patch(
                "servey.finder.action_finder_abc.find_actions",
                return_value=[get_action(ping), get_action(consume_message)],
            ),
            patch(
                "servey.servey_celery.celery_config.background_invoker_config.find_event_channels_by_type",
                return_value=[channel],
            ),
            patch.dict(os.environ, dict(CELERY_BROKER="redis://localhost:6379/0")),
            patch("celery.app.task.Task.apply_async", return_value=None),
        ):
            _reload_module()
            # noinspection PyUnresolvedReferences
            app = _module.app
            next(t for t in app.tasks if t.endswith("test_celery_app.ping"))
            next(t for t in app.tasks if t.endswith("test_celery_app.consume_message"))
            channel.publish("Some message")

    def test_app_no_triggers(self):
        @action
        def pong() -> UUID:
            """No implementation required"""

        with (
            patch(
                "servey.finder.action_finder_abc.find_actions",
                return_value=[get_action(pong)],
            ),
            patch(
                "servey.servey_celery.celery_config.background_invoker_config.find_event_channels_by_type",
                return_value=[],
            ),
            patch.dict(os.environ, dict(CELERY_BROKER="redis://localhost:6379/0")),
            patch("celery.app.task.Task.apply_async", return_value=None),
        ):
            _reload_module()
            # noinspection PyUnresolvedReferences
            app = _module.app
            self.assertIsNone(
                next((t for t in app.tasks if t.endswith("test_celery_app.pong")), None)
            )

    def test_on_after_connect(self):
        @action(triggers=(FixedRateTrigger(10),))
        def ping() -> UUID:
            """No implementation required"""

        class MockOnAfterConfigure:
            def __init__(self):
                self.fn = None

            def connect(self, fn):
                assert self.fn is None
                assert fn is not None
                self.fn = fn

        ns = {}

        class MockTask:
            @staticmethod
            def s():
                return "foobar"

        class MockCeleryApp:
            def __init__(self):
                self.task_called = 0
                self.periodic_called = 0
                self.on_after_configure = MockOnAfterConfigure()

            def task(self, fn):
                self.task_called += 1
                assert fn == ping
                return MockTask

            def add_periodic_task(self, interval, s):
                self.periodic_called += 1
                assert interval == 10
                assert s == "foobar"

        with patch(
            "servey.servey_celery.celery_config.fixed_rate_trigger_config.find_actions_with_trigger_type",
            return_value=[(get_action(ping), FixedRateTrigger(10))],
        ):
            app = MockCeleryApp()
            config = FixedRateTriggerConfig()
            config.configure(app, ns)
            self.assertEqual(app.task_called, 1)
            app.on_after_configure.fn(app)
            self.assertEqual(app.periodic_called, 1)


_module = None


def _reload_module():
    global _module
    if _module:
        importlib.reload(_module)
    else:
        from servey.servey_celery import celery_app

        _module = celery_app
