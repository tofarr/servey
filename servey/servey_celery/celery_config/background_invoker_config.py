from typing import Dict

from celery import Celery

from servey.event_channel.background.background_action_channel import (
    BackgroundActionChannel,
)
from servey.finder.event_channel_finder_abc import find_channels_by_type
from servey.servey_celery.celery_config.celery_config_abc import CeleryConfigABC


class BackgroundInvokerConfig(CeleryConfigABC):
    def configure(self, app: Celery, global_ns: Dict):
        for channel in find_channels_by_type(BackgroundActionChannel):
            if channel.name not in global_ns:
                fn = channel.fn
                global_ns[channel.name] = app.task(fn)
