from typing import Dict

from celery import Celery
from kombu.common import Broadcast

from servey.event_channel.websocket.websocket_event_channel import (
    WebsocketEventChannel,
    T,
)
from servey.finder.event_channel_finder_abc import find_event_channels_by_type
from servey.servey_celery.celery_config.celery_config_abc import CeleryConfigABC
from servey.servey_starlette.event_channel.starlette_websocket_sender_factory import (
    StarletteWebsocketSenderFactory,
)


class WebsocketConfig(CeleryConfigABC):
    def configure(self, app: Celery, global_ns: Dict):
        websocket_channels = list(find_event_channels_by_type(WebsocketEventChannel))
        if not websocket_channels:
            return
        factory = StarletteWebsocketSenderFactory()
        channels_by_name = {
            c.name: factory.create(
                channel_name=c.name,
                event_schema=c.event_schema,
                access_control=c.access_control,
                event_filter=c.event_filter,
            )
            for c in websocket_channels
        }

        def servey_websocket_broadcast(channel_name: str, event: T):
            channel = channels_by_name[channel_name]
            channel.send(channel_name, event)

        global_ns["servey_websocket_broadcast"] = app.task(servey_websocket_broadcast)
        app.conf.task_queues = Broadcast("servey_websocket_broadcast")
