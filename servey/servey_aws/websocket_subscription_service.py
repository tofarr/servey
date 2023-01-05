import json
import os
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict

import boto3
from boto3.dynamodb.conditions import Key
from marshy import get_default_context
from marshy.marshaller.marshaller_abc import MarshallerABC

from servey.security.access_control.allow_none import ALLOW_NONE
from servey.security.authorization import Authorization
from servey.servey_aws import is_lambda_env
from servey.subscription.subscription import Subscription, T
from servey.subscription.subscription_service import (
    SubscriptionServiceFactoryABC,
    SubscriptionServiceABC,
)


@dataclass
class AWSWebsocketSubscriptionService(SubscriptionServiceABC):
    connection_table: Any = field(
        default_factory=lambda: boto3.resource("dynamodb").Table(
            os.environ["CONNECTION_TABLE_NAME"]
        )
    )
    apis_by_endpoint_url: Dict[str, Any] = field(default_factory=dict)
    authorization_marshaller: MarshallerABC[Authorization] = field(
        default_factory=lambda: get_default_context().get_marshaller(
            Optional[Authorization]
        )
    )

    def get_api_for_endpoint(self, endpoint_url: str):
        api = self.apis_by_endpoint_url.get(endpoint_url)
        if not api:
            api = boto3.client("apigatewaymanagementapi", endpoint_url=endpoint_url)
            self.apis_by_endpoint_url[endpoint_url] = api
        return api

    def publish(self, subscription: Subscription[T], event: T):
        data = json.dumps(subscription.event_marshaller.dump(event)).encode("utf-8")
        kwargs = dict(
            Select="SPECIFIC_ATTRIBUTES",
            ProjectionExpression="connection_id,endpoint_url,user_authorization",
            IndexName="gsi__subscription_name__connection_id",
            KeyConditionExpression=Key("subscription_name").eq(subscription.name),
        )
        while True:
            response = self.connection_table.query(**kwargs)
            items = response.get("Items") or []
            for item in items:
                api = self.get_api_for_endpoint(item["endpoint_url"])
                if subscription.event_filter:
                    user_authorization = item.get("user_authorization")
                    if user_authorization:
                        user_authorization = self.authorization_marshaller.load(
                            user_authorization
                        )
                    if not subscription.event_filter.should_publish(
                        event, user_authorization
                    ):
                        continue
                api.post_to_connection(Data=data, ConnectionId=item["connection_id"])
            kwargs["ExclusiveStartKey"] = response.get("LastEvaluatedKey")
            if not kwargs["ExclusiveStartKey"]:
                break


class AWSWebsocketSubscriptionServiceFactory(SubscriptionServiceFactoryABC):
    def create(
        self, subscriptions: List[Subscription]
    ) -> Optional[SubscriptionServiceABC]:
        if not is_lambda_env():
            return
        subscribable = [s for s in subscriptions if s.access_control != ALLOW_NONE]
        if subscribable:
            return AWSWebsocketSubscriptionService()
