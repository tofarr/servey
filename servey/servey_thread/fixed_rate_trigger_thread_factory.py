import logging
from typing import Iterator
from threading import Thread

from servey.finder.action_finder_abc import find_actions_with_trigger_type
from servey.servey_thread.fixed_rate_trigger_thread import FixedRateTriggerThread
from servey.servey_thread.thread_factory_abc import ThreadFactoryABC
from servey.trigger.fixed_rate_trigger import FixedRateTrigger

_LOGGER = logging.getLogger(__name__)


class FixedRateTriggerThreadFactory(ThreadFactoryABC):
    """
    Factory for threads when running in threaded mode
    """

    def create_threads(self, daemon: bool) -> Iterator[Thread]:
        for action, trigger in find_actions_with_trigger_type(FixedRateTrigger):
            _LOGGER.info(f"Starting: {action.name}")
            t = FixedRateTriggerThread(action.fn, trigger, daemon)
            yield t
            t.start()
