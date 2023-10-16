import os
from unittest import TestCase
from unittest.mock import patch

from servey.action.action import action, get_action
from servey.event_channel.background.background_action_channel import (
    background_action_channel,
)
from servey.servey_aws.sqs_background_invoker import SqsBackgroundInvokerFactory


class TestSqsBackgroundInvoker(TestCase):
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
                self.assertEqual("servey_main-dummy_channel", QueueName)
                return {"QueueUrl": "https://foobar.com"}

            @staticmethod
            def send_message(QueueUrl: str, MessageBody: str):
                messages.append(dict(queue_url=QueueUrl, body=MessageBody))

        messages = []
        channel = background_action_channel(mock_consumer, name="dummy_channel")
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
            factory = SqsBackgroundInvokerFactory()
            invoker = factory.create(get_action(mock_consumer), "dummy_channel")
            invoker.invoke(13)
            self.assertEqual(
                [{"body": "13", "queue_url": "https://foobar.com"}], messages
            )
