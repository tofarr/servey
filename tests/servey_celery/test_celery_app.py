import importlib
import os
from unittest import TestCase
from unittest.mock import patch
from uuid import UUID

from servey.action.action import action, get_action
from servey.subscription.subscription import subscription
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

        subscription_ = subscription(
            str,
            name="message_broadcaster",
            action_subscribers=(get_action(consume_message),),
        )

        with (
            patch(
                "servey.finder.action_finder_abc.find_actions",
                return_value=[get_action(ping), get_action(consume_message)],
            ),
            patch(
                "servey.servey_celery.celery_config.subscription_config.find_subscriptions",
                return_value=[subscription_],
            ),
            patch.dict(os.environ, dict(CELERY_BROKER="redis://localhost:6379/0")),
            patch("celery.app.task.Task.apply_async", return_value=None),
        ):
            _reload_module()
            # noinspection PyUnresolvedReferences
            app = _module.app
            next(t for t in app.tasks if t.endswith("test_celery_app.ping"))
            next(t for t in app.tasks if t.endswith("test_celery_app.consume_message"))
            subscription_.publish("Some message")
            print(app)

    def test_app_no_triggers(self):
        @action
        def ping() -> UUID:
            """No implementation required"""

        with (
            patch(
                "servey.finder.action_finder_abc.find_actions",
                return_value=[get_action(ping)],
            ),
            patch(
                "servey.servey_celery.celery_config.subscription_config.find_subscriptions",
                return_value=[],
            ),
            patch.dict(os.environ, dict(CELERY_BROKER="redis://localhost:6379/0")),
            patch("celery.app.task.Task.apply_async", return_value=None),
        ):
            _reload_module()
            # noinspection PyUnresolvedReferences
            app = _module.app
            app.on_after_configure.connect()
            next(t for t in app.tasks if t.endswith("test_celery_app.ping"))


_module = None


def _reload_module():
    global _module
    if _module:
        importlib.reload(_module)
    else:
        from servey.servey_celery import celery_app

        _module = celery_app
