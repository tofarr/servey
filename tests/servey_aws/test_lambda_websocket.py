import importlib
import json
import os
from unittest import TestCase
from unittest.mock import patch, MagicMock

from servey.security.authorization import ROOT
from servey.subscription.subscription import subscription
from tests.servey_strawberry.test_schema_factory import NumberStats


class TestLambdaWebsocket(TestCase):
    def test_connect(self):
        mock_resource = MagicMock()
        with (
            patch("boto3.resource", mock_resource),
            patch.dict(
                os.environ,
                {
                    "AWS_REGION": "bezos-moon-base",
                    "CONNECTION_TABLE_NAME": "mock_connections",
                },
            ),
        ):
            from servey.servey_aws import lambda_websocket

            importlib.reload(lambda_websocket)
            lambda_websocket.lambda_handler(
                {
                    "requestContext": {
                        "connectionId": "connection_1",
                        "routeKey": "$connect",
                        "domainName": "foobar.com",
                        "stage": "dev",
                    },
                    "headers": {
                        "Authorization": f"Bearer {lambda_websocket._AUTHORIZER.encode(ROOT)}"
                    },
                },
                None,
            )
            lambda_websocket.lambda_handler(
                {
                    "requestContext": {
                        "connectionId": "connection_2",
                        "routeKey": "$connect",
                        "domainName": "foobar2.com",
                        "stage": "dev",
                    }
                },
                None,
            )

            table = mock_resource.return_value.Table
            table.assert_called_with("mock_connections")
            put_item = table.return_value.put_item
            put_item_call_list = [a.kwargs["Item"] for a in put_item.call_args_list]
            expected = [
                {
                    "connection_id": "connection_1",
                    "subscription_name": " ",
                    "user_authorization": {
                        "subject_id": None,
                        "scopes": ["root"],
                        "not_before": None,
                        "expire_at": None,
                    },
                    "updated_at": put_item_call_list[0]["updated_at"],
                },
                {
                    "connection_id": "connection_2",
                    "subscription_name": " ",
                    "user_authorization": None,
                    "updated_at": put_item_call_list[1]["updated_at"],
                },
            ]
            self.assertEqual(expected, put_item_call_list)

    def test_disconnect(self):
        mock_resource = MagicMock()
        items = [
            {"connection_id": "connection_1", "subscription_name": " "},
            {"connection_id": "connection_1", "subscription_name": "foo"},
            {"connection_id": "connection_1", "subscription_name": "bar"},
        ]
        mock_resource.return_value.Table.return_value.query.return_value = {
            "Items": items,
        }
        with (
            patch("boto3.resource", mock_resource),
            patch.dict(
                os.environ,
                {
                    "AWS_REGION": "bezos-moon-base",
                    "CONNECTION_TABLE_NAME": "mock_connections",
                },
            ),
        ):
            from servey.servey_aws import lambda_websocket

            importlib.reload(lambda_websocket)
            result = lambda_websocket.lambda_handler(
                {
                    "requestContext": {
                        "connectionId": "connection_1",
                        "routeKey": "$disconnect",
                        "domainName": "foobar.com",
                        "stage": "dev",
                    },
                },
                None,
            )
            self.assertEqual({"statusCode": 200}, result)
            table = mock_resource.return_value.Table.return_value
            delete_item = (
                table.batch_writer.return_value.__enter__.return_value.delete_item
            )
            delete_item_call_list = [
                a.kwargs["Key"] for a in delete_item.call_args_list
            ]
            self.assertEqual(items, delete_item_call_list)

    def test_subscribe(self):
        subscription_ = subscription(NumberStats, "number_stats")
        mock_resource = MagicMock()
        item = {"connection_id": "connection_1", "subscription_name": " "}
        table = mock_resource.return_value.Table.return_value
        table.get_item.return_value = item
        with (
            patch("boto3.resource", mock_resource),
            patch.dict(
                os.environ,
                {
                    "AWS_REGION": "bezos-moon-base",
                    "CONNECTION_TABLE_NAME": "mock_connections",
                },
            ),
            patch(
                "servey.finder.subscription_finder_abc.find_subscriptions",
                return_value=[subscription_],
            ),
        ):
            from servey.servey_aws import lambda_websocket

            importlib.reload(lambda_websocket)
            result = lambda_websocket.lambda_handler(
                {
                    "requestContext": {
                        "connectionId": "connection_1",
                        "routeKey": "$default",
                        "domainName": "foobar.com",
                        "stage": "dev",
                    },
                    "body": json.dumps(
                        {"type": "Subscribe", "payload": "number_stats"}
                    ),
                },
                None,
            )
            self.assertEqual({"statusCode": 200}, result)
            put_item = mock_resource.return_value.Table.return_value.put_item
            put_item_call_list = [a.kwargs["Item"] for a in put_item.call_args_list]
            self.assertEqual(
                [
                    {
                        "connection_id": "connection_1",
                        "subscription_name": "number_stats",
                        "endpoint_url": "https://foobar.com/dev",
                        "updated_at": put_item_call_list[0]["updated_at"],
                        "user_authorization": None,
                    }
                ],
                put_item_call_list,
            )

    def test_unsubscribe(self):
        subscription_ = subscription(NumberStats, "number_stats")
        mock_resource = MagicMock()
        with (
            patch("boto3.resource", mock_resource),
            patch.dict(
                os.environ,
                {
                    "AWS_REGION": "bezos-moon-base",
                    "CONNECTION_TABLE_NAME": "mock_connections",
                },
            ),
            patch(
                "servey.finder.subscription_finder_abc.find_subscriptions",
                return_value=[subscription_],
            ),
        ):
            from servey.servey_aws import lambda_websocket

            importlib.reload(lambda_websocket)
            result = lambda_websocket.lambda_handler(
                {
                    "requestContext": {
                        "connectionId": "connection_1",
                        "routeKey": "$default",
                        "domainName": "foobar.com",
                        "stage": "dev",
                    },
                    "body": json.dumps(
                        {"type": "Unsubscribe", "payload": "number_stats"}
                    ),
                },
                None,
            )
            self.assertEqual({"statusCode": 200}, result)
            delete_item = mock_resource.return_value.Table.return_value.delete_item
            delete_item_call_list = [
                a.kwargs["Key"] for a in delete_item.call_args_list
            ]
            self.assertEqual(
                [
                    {
                        "connection_id": "connection_1",
                        "subscription_name": "number_stats",
                    }
                ],
                delete_item_call_list,
            )

    def test_invalid_body(self):
        subscription_ = subscription(NumberStats, "number_stats")
        mock_resource = MagicMock()
        with (
            patch("boto3.resource", mock_resource),
            patch.dict(
                os.environ,
                {
                    "AWS_REGION": "bezos-moon-base",
                    "CONNECTION_TABLE_NAME": "mock_connections",
                },
            ),
            patch(
                "servey.finder.subscription_finder_abc.find_subscriptions",
                return_value=[subscription_],
            ),
        ):
            from servey.servey_aws import lambda_websocket

            importlib.reload(lambda_websocket)
            response = lambda_websocket.lambda_handler(
                {
                    "requestContext": {
                        "connectionId": "connection_1",
                        "routeKey": "$default",
                        "domainName": "foobar.com",
                        "stage": "dev",
                    },
                    "body": "This is not valid",
                },
                None,
            )
            self.assertEqual({"statusCode": 400}, response)
