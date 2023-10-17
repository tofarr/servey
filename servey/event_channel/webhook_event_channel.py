from dataclasses import dataclass, field
from typing import Optional, Dict

import requests
from marshy import ExternalType
from marshy.marshaller.marshaller_abc import MarshallerABC
from schemey import Schema

from servey.event_channel.event_channel_abc import EventChannelABC, T
from servey.trigger.web_trigger import WebTriggerMethod


@dataclass(frozen=True)
class WebhookEventChannel(EventChannelABC[T]):
    """
    Publisher which passes an event_channel to a web hook
    """

    url: str
    event_marshaller: MarshallerABC[T]
    event_schema: Optional[Schema]
    method: WebTriggerMethod = WebTriggerMethod.POST
    headers: Optional[Dict[str, str]] = field(
        default_factory=lambda: {"ContentType": "application/json"}
    )
    description: Optional[str] = None
    timeout: int = 5

    def publish(self, event: ExternalType):
        dumped = self.event_marshaller.dump(event)
        if self.event_schema:
            self.event_schema.validate(dumped)
        requests.request(
            self.url,
            self.method.value,
            headers=self.headers,
            json=dumped,
            timeout=self.timeout,
        )
