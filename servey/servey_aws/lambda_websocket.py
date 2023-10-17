import json
import logging
import os
from datetime import datetime
from typing import Optional

import boto3
from boto3.dynamodb.conditions import Key
from marshy import get_default_context
from marshy.types import ExternalItemType, ExternalType

from servey.event_channel.websocket.websocket_event_channel import WebsocketEventChannel
from servey.finder.event_channel_finder_abc import find_event_channels_by_type
from servey.security.authorization import Authorization
from servey.security.authorizer.authorizer_factory_abc import get_default_authorizer

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)
_DYNAMODB_TABLE = boto3.resource("dynamodb").Table(os.environ["CONNECTION_TABLE_NAME"])
_CHANNELS = list(find_event_channels_by_type(WebsocketEventChannel))
_AUTH_MARSHALLER = get_default_context().get_marshaller(Optional[Authorization])
_AUTHORIZER = get_default_authorizer()


# pylint: disable=W0613
# noinspection PyUnusedLocal
def lambda_handler(event: ExternalItemType, context) -> ExternalType:
    _LOGGER.info(json.dumps({"lambda_event": event}))
    request_context = event.get("requestContext") or {}
    route_key = request_context.get("routeKey")
    connection_id = request_context.get("connectionId")
    endpoint_url = f"https://{request_context['domainName']}/{request_context['stage']}"
    status_code = 400
    if route_key == "$connect":
        user_authorization = None
        authorization_header = (event.get("headers") or {}).get("Authorization")
        if authorization_header and authorization_header.lower().startswith("bearer "):
            user_authorization = _AUTHORIZER.authorize(authorization_header[7:])
        connect(connection_id, user_authorization)
        status_code = 200
    elif route_key == "$disconnect":
        disconnect(connection_id)
        status_code = 200
    else:
        try:
            body = json.loads(event["body"])
            type_ = body["type"]
            channel_name = body["payload"]
            # Ensure channel exists
            channel = next(c for c in _CHANNELS if c.name == channel_name)
            if type_ == "Subscribe":
                subscribe(connection_id, channel.name, endpoint_url)
                status_code = 200
            elif type_ == "Unsubscribe":
                unsubscribe(connection_id, channel.name)
                status_code = 200
        except Exception as e:
            _LOGGER.warning(f"error_handling_websocket:{e}")
    response = {"statusCode": status_code}
    return response


def connect(connection_id: str, user_authorization: Authorization):
    _DYNAMODB_TABLE.put_item(
        Item={
            "connection_id": connection_id,
            "subscription_name": " ",
            "user_authorization": _AUTH_MARSHALLER.dump(user_authorization),
            "updated_at": datetime.now().isoformat(),
        }
    )


def disconnect(connection_id: str):
    keys = []
    kwargs = {
        "Select": "SPECIFIC_ATTRIBUTES",
        "ProjectionExpression": "connection_id,subscription_name",
        "KeyConditionExpression": Key("connection_id").eq(connection_id),
    }
    while True:
        response = _DYNAMODB_TABLE.query(**kwargs)
        keys.extend(response["Items"])
        kwargs["ExclusiveStartKey"] = response.get("LastEvaluatedKey")
        if not kwargs["ExclusiveStartKey"]:
            break

    with _DYNAMODB_TABLE.batch_writer() as batch:
        for key in keys:
            batch.delete_item(Key=key)


def subscribe(connection_id: str, subscription_name: str, endpoint_url: str):
    item = _DYNAMODB_TABLE.get_item(
        Key={"connection_id": connection_id, "subscription_name": " "}
    )
    _DYNAMODB_TABLE.put_item(
        Item={
            "connection_id": connection_id,
            "subscription_name": subscription_name,
            "endpoint_url": endpoint_url,
            "user_authorization": item.get("user_authorization"),
            "updated_at": datetime.now().isoformat(),
        }
    )


def unsubscribe(connection_id: str, subscription_name: str):
    key = {"connection_id": connection_id, "subscription_name": subscription_name}
    _DYNAMODB_TABLE.delete_item(Key=key)
