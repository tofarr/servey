"""
This module sets up a celery app using any default Action with a FixedRateTrigger
to be run from a celery worker.
All such actions are added to the global namespace as celery tasks.
Celery supports use of rabbitmq, redis, and even sqs.

Example:
    This example contains 3 processes:
        * A rabbitmq message broker process
        * A celery worker process
        * A celery beat scheduler process

    Rabbitmq is available through docker using `docker run -d -p 5672:5672 rabbitmq`. It should start automatically
    when downloaded (You can also restart it in the docker console)

    In a terminal, start a celery worker process with :
        `celery -A servey.servey_celery.celery_app worker --loglevel=INFO`

    In a second terminal, start a celery beat scheduler with:
        `celery -A servey.servey_celery.celery_app beat --loglevel=INFO`

    Log output for scheduled tasks should appear in the output for the worker.

"""
import logging
import os
from celery import Celery

# Setup app and tasks...
from servey.finder.action_finder_abc import find_actions_with_trigger_type
from servey.finder.subscription_finder_abc import find_subscriptions
from servey.trigger.fixed_rate_trigger import FixedRateTrigger

_CELERY_BROKER = os.environ.get("CELERY_BROKER")
_LOGGER = logging.getLogger(__name__)
_LOGGER.info(f"Starting celery with broker {_CELERY_BROKER}")
app = Celery(broker=_CELERY_BROKER)
for _action, _ in find_actions_with_trigger_type(FixedRateTrigger):
    globals()[_action.name] = app.task(_action.fn)

for _subscription in find_subscriptions():
    if _subscription.action_subscribers:
        for _action in _subscription.action_subscribers:
            if _action.name not in globals():
                globals()[_action.name] = app.task(_action.fn)


# noinspection PyUnusedLocal
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    for action, trigger in find_actions_with_trigger_type(FixedRateTrigger):
        task = globals()[action.name]
        sender.add_periodic_task(trigger.interval, task.s())
