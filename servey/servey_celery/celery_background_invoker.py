from dataclasses import dataclass
from typing import Optional

from servey.action.action import Action
from servey.event_channel.background.background_invoker_abc import (
    BackgroundInvokerABC,
    T,
    BackgroundInvokerFactoryABC,
)


@dataclass
class CeleryBackgroundInvoker(BackgroundInvokerABC):
    name: str

    def invoke(self, event: T, delay: int = 0):
        from servey.servey_celery import celery_app

        task = getattr(celery_app, self.name)
        task.delay(*[event], countdown=delay)


class CeleryBackgroundInvokerFactory(BackgroundInvokerFactoryABC):
    def create(self, action: Action, name: str) -> Optional[BackgroundInvokerABC]:
        from servey.servey_celery import has_celery_broker

        if has_celery_broker():
            return CeleryBackgroundInvoker(name)
