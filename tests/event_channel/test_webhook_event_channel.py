from unittest import TestCase
from unittest.mock import MagicMock, patch, call

from marshy.marshaller import NoOpMarshaller
from schemey.schema import str_schema

from servey.event_channel.webhook_event_channel import WebhookEventChannel


class TestWebhookEventChannel(TestCase):
    def test_publish(self):
        channel = WebhookEventChannel(
            "foobar", "https://foobar.com", NoOpMarshaller(str), str_schema()
        )
        mock = MagicMock()
        with patch("servey.event_channel.webhook_event_channel.requests", mock):
            channel.publish("Some event")
        self.assertEqual(
            mock.request.mock_calls,
            [
                call(
                    "https://foobar.com",
                    "post",
                    headers={"ContentType": "application/json"},
                    json="Some event",
                    timeout=5,
                )
            ],
        )
