import json
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any

import boto3

from servey.servey_aws import is_lambda_env
from servey.subscription.subscription import Subscription, T
from servey.subscription.subscription_service import (
    SubscriptionServiceABC,
    SubscriptionServiceFactoryABC,
)
from servey.util import get_servey_main


@dataclass
class SqsSubscriptionService(SubscriptionServiceABC):
    """Subscription service backed by SQS."""

    queue_names_by_subscription_name: Dict[str, str]
    sqs_client: Any = field(default_factory=lambda: boto3.client("sqs"))
    queue_urls_by_queue_name: Dict[str, Optional[str]] = field(default_factory=dict)

    def get_queue_url(self, subscription_name: str) -> Optional[str]:
        queue_name = self.queue_names_by_subscription_name.get(subscription_name)
        if not queue_name:
            return
        queue_url = self.queue_urls_by_queue_name.get(queue_name)
        if not queue_url:
            response = self.sqs_client.get_queue_url(QueueName=queue_name)
            queue_url = self.queue_urls_by_queue_name[queue_name] = response["QueueUrl"]
        return queue_url

    def publish(self, subscription: Subscription[T], event: T):
        queue_url = self.get_queue_url(subscription.name)
        if queue_url:
            self.sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=json.dumps(subscription.event_marshaller.dump(event)),
            )


class SqsSubscriptionServiceFactory(SubscriptionServiceFactoryABC):
    def create(
        self, subscriptions: List[Subscription]
    ) -> Optional[SubscriptionServiceABC]:
        if not is_lambda_env():
            return
        queue_names_by_subscription_name = {}
        service_name = get_servey_main()
        for subscription in subscriptions:
            if subscription.action_subscribers:
                queue_name = service_name + "-" + subscription.name
                queue_names_by_subscription_name[subscription.name] = queue_name
        if queue_names_by_subscription_name:
            return SqsSubscriptionService(queue_names_by_subscription_name)
