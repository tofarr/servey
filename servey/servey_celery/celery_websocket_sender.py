from typing import Optional

from schemey import Schema

from servey.event_channel.websocket.event_filter_abc import EventFilterABC
from servey.event_channel.websocket.websocket_sender import (
    WebsocketSenderFactoryABC,
    WebsocketSenderABC,
    T,
)
from servey.security.access_control.access_control_abc import AccessControlABC
from servey.security.access_control.allow_all import ALLOW_ALL


class CeleryWebsocketSender(WebsocketSenderABC):
    def send(self, channel_name: str, event: T):
        from servey.servey_celery import celery_app

        task = getattr(celery_app, "servey_websocket_broadcast")
        task.delay(*[channel_name, event])


class CeleryWebsocketSenderFactory(WebsocketSenderFactoryABC):
    priority = 120

    def create(
        self,
        channel_name: str,
        event_schema: Schema,
        access_control: AccessControlABC = ALLOW_ALL,
        event_filter: Optional[EventFilterABC] = None,
    ) -> Optional[WebsocketSenderABC]:
        from servey.servey_celery import has_celery_broker

        if has_celery_broker():
            return CeleryWebsocketSender()
