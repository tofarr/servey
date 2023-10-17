import json
import os
from dataclasses import dataclass, field
from typing import Optional, Any, Dict

import boto3
from boto3.dynamodb.conditions import Key
from marshy import get_default_context
from marshy.marshaller.marshaller_abc import MarshallerABC
from schemey import Schema

from servey.event_channel.websocket.event_filter_abc import EventFilterABC
from servey.event_channel.websocket.websocket_sender import (
    WebsocketSenderABC,
    T,
    WebsocketSenderFactoryABC,
)
from servey.security.access_control.access_control_abc import AccessControlABC
from servey.security.access_control.allow_all import ALLOW_ALL
from servey.security.authorization import Authorization
from servey.servey_aws import is_lambda_env


@dataclass
class AWSWebsocketSender(WebsocketSenderABC[T]):
    event_marshaller: MarshallerABC[T]
    event_filter: Optional[EventFilterABC] = None
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

    def send(self, channel_name: str, event: T):
        kwargs = {
            "Select": "SPECIFIC_ATTRIBUTES",
            "ProjectionExpression": "connection_id,endpoint_url,user_authorization",
            "IndexName": "gsi__subscription_name__connection_id",
            "KeyConditionExpression": Key("subscription_name").eq(channel_name),
        }
        while True:
            response = self.connection_table.query(**kwargs)
            items = response.get("Items") or []
            for item in items:
                api = self.get_api_for_endpoint(item["endpoint_url"])
                if self.event_filter:
                    user_authorization = item.get("user_authorization")
                    if user_authorization:
                        user_authorization = self.authorization_marshaller.load(
                            user_authorization
                        )
                    if not self.event_filter.should_publish(event, user_authorization):
                        continue
                data = json.dumps(self.event_marshaller.dump(event)).encode("utf-8")
                api.post_to_connection(Data=data, ConnectionId=item["connection_id"])
            kwargs["ExclusiveStartKey"] = response.get("LastEvaluatedKey")
            if not kwargs["ExclusiveStartKey"]:
                break


class AWSWebsocketSenderFactory(WebsocketSenderFactoryABC):
    priority: int = 150

    def create(
        self,
        channel_name: str,
        event_schema: Schema,
        access_control: AccessControlABC = ALLOW_ALL,
        event_filter: Optional[EventFilterABC] = None,
    ) -> Optional[WebsocketSenderABC]:
        if not is_lambda_env():
            return
        return AWSWebsocketSender(
            event_marshaller=get_default_context().get_marshaller(
                event_schema.python_type
            ),
            event_filter=event_filter,
        )
