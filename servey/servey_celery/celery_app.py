"""
This module sets up a celery app using any default Action with a FixedRateTrigger
to be run from a celery worker.
All such actions are added to the global namespace as celery tasks
Run this with `celery -A servey.servey_celery.celery_app worker --loglevel=INFO`
"""
import logging
import os
from celery import Celery

# Setup app and tasks...
from servey.action.finder.action_finder_abc import find_actions_with_trigger_type
from servey.action.trigger.fixed_rate_trigger import FixedRateTrigger

_CELERY_BROKER = os.environ.get("CELERY_BROKER")
_LOGGER = logging.getLogger(__name__)
_LOGGER.info(f"Starting celery with broker {_CELERY_BROKER}")
app = Celery(broker=_CELERY_BROKER)
for _action, _ in find_actions_with_trigger_type(FixedRateTrigger):
    globals()[_action.action_meta.name] = app.task(_action)


# noinspection PyUnusedLocal
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    for action, trigger in find_actions_with_trigger_type(FixedRateTrigger):
        task = globals()[action.action_meta.name]
        sender.add_periodic_task(trigger.interval, task.s())
