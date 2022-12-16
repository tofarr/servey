"""
App for case where servey is run in local schedule mode. Scheduled events are run using
threads (As opposed to Celery).
Run this with `python -m servey.servey_thread`
"""
import logging
import os

from servey.finder.action_finder_abc import find_actions_with_trigger_type
from servey.trigger.fixed_rate_trigger import FixedRateTrigger
from servey.servey_thread.fixed_rate_trigger_thread import FixedRateTriggerThread

LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
logging.basicConfig(level=LOGLEVEL)
_LOGGER = logging.getLogger(__name__)
DAEMON = (os.environ.get("SERVEY_DAEMON") or "").lower() in ("t", "true", "1")
_THREADS = []
_LOGGER.info("Starting threads for actions...")
for action, trigger in find_actions_with_trigger_type(FixedRateTrigger):
    _LOGGER.info(f"Starting: {action.name}")
    t = FixedRateTriggerThread(action.fn, trigger, DAEMON)
    _THREADS.append(t)
    t.start()
