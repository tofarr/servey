import time
from threading import Thread
from typing import Callable

from servey.trigger.fixed_rate_trigger import FixedRateTrigger


class FixedRateTriggerThread(Thread):
    def __init__(
        self, fn: Callable, fixed_rate_trigger: FixedRateTrigger, daemon: bool
    ):
        Thread.__init__(self, daemon=daemon)
        self.fn = fn
        self.fixed_rate_trigger = fixed_rate_trigger

    def run(self):
        while True:
            time.sleep(self.fixed_rate_trigger.interval)
            self.fn()
