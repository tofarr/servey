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

from marshy.factory.impl_marshaller_factory import get_impls
from servey.servey_celery.celery_config.celery_config_abc import CeleryConfigABC

# Setup app and tasks...
_CELERY_BROKER = os.environ.get("CELERY_BROKER")
_LOGGER = logging.getLogger(__name__)
_LOGGER.info(f"Starting celery with broker {_CELERY_BROKER}")
app = Celery(broker=_CELERY_BROKER)
for impl in get_impls(CeleryConfigABC):
    impl().configure(app, globals())
