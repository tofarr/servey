import inspect
import json
from dataclasses import dataclass, field
from typing import Optional, Any

import boto3
from marshy import get_default_context
from marshy.marshaller.marshaller_abc import MarshallerABC

from servey.action.action import Action
from servey.event_channel.background.background_invoker_abc import (
    BackgroundInvokerABC,
    BackgroundInvokerFactoryABC,
    T,
)
from servey.servey_aws import is_lambda_env
from servey.util import get_servey_main


@dataclass
class SqsSBackgroundInvoker(BackgroundInvokerABC[T]):
    """Subscription service backed by SQS."""

    action: Action
    event_marshaller: MarshallerABC[T]
    queue_name: str
    queue_url: Optional[str] = None
    sqs_client: Any = field(default_factory=lambda: boto3.client("sqs"))

    def get_queue_url(self) -> Optional[str]:
        queue_url = self.queue_url
        if not queue_url:
            response = self.sqs_client.get_queue_url(QueueName=self.queue_name)
            queue_url = self.queue_url = response["QueueUrl"]
        return queue_url

    def invoke(self, event: T, delay: int = 0):
        queue_url = self.get_queue_url()
        kwargs = {
            "QueueUrl": queue_url,
            "MessageBody": json.dumps(self.event_marshaller.dump(event)),
        }
        if delay:
            kwargs["DelaySeconds"] = delay
        self.sqs_client.send_message(**kwargs)


class SqsBackgroundInvokerFactory(BackgroundInvokerFactoryABC):
    def create(self, action: Action, name: str) -> Optional[BackgroundInvokerABC]:
        if not is_lambda_env():
            return
        service_name = get_servey_main()
        sig = inspect.signature(action.fn)
        params = list(sig.parameters.values())
        if len(params) != 1:
            return  # Sqs requires a single event_channel
        event_type = params[0].annotation
        return SqsSBackgroundInvoker(
            action=action,
            event_marshaller=get_default_context().get_marshaller(event_type),
            queue_name=service_name + "-" + name,
        )
