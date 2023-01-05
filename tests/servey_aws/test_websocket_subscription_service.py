import os
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from unittest import TestCase
from unittest.mock import patch

from boto3.dynamodb.conditions import Key
from marshy import dump
from schemey.util import filter_none

from servey.security.authorization import ROOT, Authorization
from servey.servey_aws.websocket_subscription_service import (
    AWSWebsocketSubscriptionServiceFactory,
)
from servey.subscription.event_filter_abc import EventFilterABC
from servey.subscription.subscription import subscription


class TestWebsocketSubscriptionService(TestCase):
    def test_connect_and_publish(self):
        mock_api = MockApiGatewayManagementApi()

        def mock_boto3_client(name: str, endpoint_url: str):
            self.assertEqual("apigatewaymanagementapi", name)
            self.assertEqual("https://moon-base.com", endpoint_url)
            return mock_api

        def mock_boto3_resource(name: str):
            self.assertEqual("dynamodb", name)
            return MockDynamodbTableFactory()

        class MyEventFilter(EventFilterABC):
            def should_publish(self, event: str, authorization: Authorization) -> bool:
                return authorization and "root" in authorization.scopes

        with (
            patch("boto3.client", mock_boto3_client),
            patch("boto3.resource", mock_boto3_resource),
            patch.dict(
                os.environ,
                {
                    "AWS_REGION": "bezos-moon-base",
                    "CONNECTION_TABLE_NAME": "mock_connections",
                },
            ),
        ):
            subscription_ = subscription(
                str, "my_messager", event_filter=MyEventFilter()
            )
            factory = AWSWebsocketSubscriptionServiceFactory()
            service = factory.create([subscription_])
            service.publish(subscription_, "Can you hear me Major Tom?")
            expected_posts = [
                {
                    "data": b'"Can you hear me Major Tom?"',
                    "connection_id": f"connection_1",
                }
            ]
            self.assertEqual(expected_posts, mock_api.posts)


@dataclass
class MockApiGatewayManagementApi:
    posts: List[Dict] = field(default_factory=list)

    def post_to_connection(self, Data: bytes, ConnectionId: str):
        self.posts.append(dict(data=Data, connection_id=ConnectionId))


@dataclass
class MockDynamodbTableFactory:
    connections: List[Dict] = field(default_factory=list)

    # noinspection PyPep8Naming
    def Table(self, table_name: str):
        assert table_name == "mock_connections"
        return MockTable(self.connections)


@dataclass
class MockTable:
    connections: List[Dict]

    @staticmethod
    def query(
        Select: str,
        ProjectionExpression: str,
        IndexName: str,
        KeyConditionExpression: Any,
        ExclusiveStartKey: Optional[str] = None,
    ):
        assert Select == "SPECIFIC_ATTRIBUTES"
        assert ProjectionExpression == "connection_id,endpoint_url,user_authorization"
        assert IndexName == "gsi__subscription_name__connection_id"
        assert KeyConditionExpression == Key("subscription_name").eq("my_messager")
        if ExclusiveStartKey:
            return {}
        else:
            return {
                "Items": [
                    filter_none(
                        {
                            "connection_id": f"connection_{i}",
                            "endpoint_url": "https://moon-base.com",
                            "user_authorization": dump(ROOT) if i == 1 else None,
                        }
                    )
                    for i in range(1, 6)
                ],
                "LastEvaluatedKey": "connection_5",
            }
