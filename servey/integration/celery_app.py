"""
This module sets up a celery app using any default Action with a FixedRateTrigger
to be run from a celery worker.
All such actions are added to the global namespace as celery tasks

Run this with `celery -A servey.integration.celery_app worker --loglevel=INFO`
"""
import os
from celery import Celery

from servey.action_context import get_default_action_context
from servey.trigger.fixed_rate_trigger import FixedRateTrigger


# Setup app and tasks...
app = Celery(broker=os.environ.get("CELERY_BROKER"))
for _action, _ in get_default_action_context().get_actions_with_trigger_type(
    FixedRateTrigger
):
    globals()[_action.action_meta.name] = app.task(_action)


# noinspection PyUnusedLocal
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    for action, trigger in get_default_action_context().get_actions_with_trigger_type(
        FixedRateTrigger
    ):
        task = globals()[action.action_meta.name]
        sender.add_periodic_task(trigger.interval, task.s())
