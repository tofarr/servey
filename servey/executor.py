import asyncio
from dataclasses import dataclass
from logging import getLogger
from typing import Optional, Any

from servey.executor_abc import ExecutorABC

logger = getLogger(__name__)


@dataclass(frozen=True)
class Executor(ExecutorABC):
    subject: Optional[Any]
    method_name: Optional[str]

    @property
    def action_meta(self):
        return self.subject.__servey_action_meta__

    def get_injection_subject(self):
        if hasattr(self.subject, "__servey_method_name__"):
            return self.subject

    def execute(self, **kwargs):
        """
        Execute this action and return the result. Local actions do not strictly enforce
        timeouts, but will instead issue a warning to the logs. Environments like lambda
        are not so forgiving, and may leave data in an invalid state!
        """
        completed = False

        def timeout_check():
            if not completed:
                logger.error(f"action_ran_too_long:{self.action_meta.name}")

        try:
            loop = asyncio.get_running_loop()
            loop.call_later(self.action_meta.timeout, timeout_check)
        except RuntimeError:
            completed = True

        try:
            if self.method_name:
                fn = getattr(self.subject, self.method_name)
            else:
                fn = self.subject
            return fn(**kwargs)
        finally:
            completed = True

    def execute_async(self, **kwargs):
        """
        Execute this action asynchronously and return flow before it finishes
        """
        loop = asyncio.get_event_loop()
        loop.call_soon(lambda: self.execute(**kwargs))
