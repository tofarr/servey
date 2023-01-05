import os
from unittest import TestCase
from unittest.mock import patch

from servey.action.action import action, get_action
from servey.servey_aws.sqs_subscription_service import SqsSubscriptionServiceFactory
from servey.subscription.subscription import subscription


class TestSqsSubscriptionService(TestCase):
    def test_publish(self):
        # noinspection PyUnusedLocal
        @action
        def mock_consumer(value: int):
            """No action required"""

        def mock_boto3_client(name: str):
            self.assertEqual("sqs", name)
            return MockSqsClient()

        class MockSqsClient:
            @staticmethod
            def get_queue_url(QueueName: str):
                self.assertEqual("servey_main-dummy_subscription", QueueName)
                return {"QueueUrl": "https://foobar.com"}

            @staticmethod
            def send_message(QueueUrl: str, MessageBody: str):
                messages.append(dict(queue_url=QueueUrl, body=MessageBody))

        messages = []
        subscription_ = subscription(
            int, "dummy_subscription", action_subscribers=(get_action(mock_consumer),)
        )
        non_sqs_subscription = subscription(int, "non_sqs")
        with (
            patch("boto3.client", mock_boto3_client),
            patch.dict(
                os.environ,
                {
                    "AWS_REGION": "bezos-moon-base",
                    "CONNECTION_TABLE_NAME": "mock_connections",
                },
            ),
        ):
            factory = SqsSubscriptionServiceFactory()
            service = factory.create([subscription_])
            service.publish(subscription_, 13)
            service.publish(non_sqs_subscription, 14)
            self.assertEqual(
                [{"body": "13", "queue_url": "https://foobar.com"}], messages
            )
