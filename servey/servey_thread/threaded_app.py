"""
App for case where servey is run in local schedule mode. Scheduled events are run using
threads (As opposed to Celery)
"""
import logging

from servey.action.finder.action_finder_abc import find_actions_with_trigger_type
from servey.action.trigger.fixed_rate_trigger import FixedRateTrigger
from servey.servey_thread.fixed_rate_trigger_thread import FixedRateTriggerThread

_LOGGER = logging.getLogger(__name__)
_THREADS = [
    FixedRateTriggerThread(action.fn, trigger)
    for action, trigger in find_actions_with_trigger_type(FixedRateTrigger)
]
