import json
import logging
import os
from datetime import datetime
from typing import Optional

import boto3
from boto3.dynamodb.conditions import Key
from marshy import get_default_context
from marshy.types import ExternalItemType, ExternalType

from servey.finder.subscription_finder_abc import find_subscriptions
from servey.security.access_control.allow_none import ALLOW_NONE
from servey.security.authorization import Authorization
from servey.security.authorizer.authorizer_factory_abc import get_default_authorizer

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)
_DYNAMODB_TABLE = boto3.resource("dynamodb").Table(os.environ["CONNECTION_TABLE_NAME"])
_SUBSCRIPTIONS = [s for s in find_subscriptions() if s.access_control != ALLOW_NONE]
_AUTH_MARSHALLER = get_default_context().get_marshaller(Optional[Authorization])
_AUTHORIZER = get_default_authorizer()


# noinspection PyUnusedLocal
def lambda_handler(event: ExternalItemType, context) -> ExternalType:
    _LOGGER.info(json.dumps(dict(lambda_event=event)))
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
            subscription_name = body["payload"]
            # Ensure subscription exists
            subscription = next(
                s for s in _SUBSCRIPTIONS if s.name == subscription_name
            )
            if type_ == "Subscribe":
                subscribe(connection_id, subscription.name, endpoint_url)
                status_code = 200
            elif type_ == "Unsubscribe":
                unsubscribe(connection_id, subscription.name)
                status_code = 200
        except Exception as e:
            _LOGGER.warning(f"error_handling_websocket:{e}")
    response = {"statusCode": status_code}
    return response


def connect(connection_id: str, user_authorization: Authorization):
    _DYNAMODB_TABLE.put_item(
        Item=dict(
            connection_id=connection_id,
            subscription_name=" ",
            user_authorization=_AUTH_MARSHALLER.dump(user_authorization),
            updated_at=datetime.now().isoformat(),
        )
    )


def disconnect(connection_id: str):
    keys = []
    kwargs = dict(
        Select="SPECIFIC_ATTRIBUTES",
        ProjectionExpression="connection_id,subscription_name",
        KeyConditionExpression=Key("connection_id").eq(connection_id),
    )
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
        Key=dict(connection_id=connection_id, subscription_name=" ")
    )
    _DYNAMODB_TABLE.put_item(
        Item=dict(
            connection_id=connection_id,
            subscription_name=subscription_name,
            endpoint_url=endpoint_url,
            user_authorization=item.get("user_authorization"),
            updated_at=datetime.now().isoformat(),
        )
    )


def unsubscribe(connection_id: str, subscription_name: str):
    key = dict(connection_id=connection_id, subscription_name=subscription_name)
    _DYNAMODB_TABLE.delete_item(Key=key)
