import importlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Callable, List
from unittest import TestCase
from unittest.mock import patch

from marshy import dump

from servey.action.action import action
from servey.action.batch_invoker import BatchInvoker
from servey.cache_control.timestamp_cache_control import TimestampCacheControl
from servey.errors import ServeyError
from servey.security.access_control.scope_access_control import ScopeAccessControl
from servey.security.authorization import Authorization, ROOT, AuthorizationError
from servey.security.authorizer.authorizer_factory_abc import get_default_authorizer
from servey.trigger.web_trigger import WEB_POST, WEB_GET, WebTriggerMethod, WebTrigger
from tests.servey_strawberry.test_schema_factory import Node


class TestLambdaInvoker(TestCase):
    def test_direct(self):
        invoker = get_invoker(get_node)
        event = dict(params=dict(name="foo"))
        result = invoker(event, None)
        expected_result = {"child_nodes": [], "name": "foo"}
        self.assertEqual(expected_result, result)

    def test_direct_with_auth(self):
        invoker = get_invoker(get_authorization)
        event = dict(params={})
        with self.assertRaises(AuthorizationError):
            invoker(event, None)

        authorizer = get_default_authorizer()
        event = dict(params={}, authorization=authorizer.encode(ROOT))
        result = invoker(event, None)
        expected_result = {
            "subject_id": None,
            "scopes": ["root"],
            "not_before": None,
            "expire_at": None,
        }
        self.assertEqual(expected_result, result)

        event = dict(params={}, authorization=dump(ROOT))
        result = invoker(event, None)
        expected_result = {
            "subject_id": None,
            "scopes": ["root"],
            "not_before": None,
            "expire_at": None,
        }
        self.assertEqual(expected_result, result)

    def test_appsync_get(self):
        invoker = get_invoker(get_node)
        event = dict(arguments=dict(name="foo"))
        result = invoker(event, None)
        expected_result = {"child_nodes": [], "name": "foo"}
        self.assertEqual(expected_result, result)

    def test_appsync_post(self):
        invoker = get_invoker(put_node)
        event = dict(arguments=dict(node=dict(name="bar")))
        result = invoker(event, None)
        self.assertEqual(True, result)
        self.assertEqual(Node("bar"), _NODES["bar"])

    def test_api_gateway_get(self):
        invoker = get_invoker(get_node)
        event = dict(httpMethod="GET", queryStringParameters=dict(name="foo"))
        result = invoker(event, None)
        # noinspection PyTypeChecker
        expected_result = {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
            },
            "body": '{"name": "foo", "child_nodes": []}',
        }
        self.assertEqual(expected_result, result)

    def test_api_gateway_post(self):
        invoker = get_invoker(put_node)
        event = dict(httpMethod="POST", body=json.dumps(dict(node=dict(name="foo"))))
        result = invoker(event, None)
        expected_result = {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": "true",
        }
        self.assertEqual(expected_result, result)

    def test_api_gateway_with_auth(self):
        invoker = get_invoker(get_authorization)
        event = dict(httpMethod="POST", body="{}")
        with self.assertRaises(AuthorizationError):
            invoker(event, None)

        authorizer = get_default_authorizer()
        event = dict(
            httpMethod="POST",
            body="{}",
            headers={"Authorization": f"Bearer {authorizer.encode(ROOT)}"},
        )
        result = invoker(event, None)
        expected_result = {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(dump(ROOT)),
        }
        self.assertEqual(expected_result, result)

    def test_api_gateway_with_caching(self):
        invoker = get_invoker(get_stored_item)
        event = dict(httpMethod="GET", queryStringParameters=dict(name="foo"))
        result = invoker(event, None)
        # noinspection PyTypeChecker,SpellCheckingInspection
        headers = {
            "Content-Type": "application/json",
            "ETag": "3g6+tMQd4iiW50nY1WFSohCR/S4DGhUbtq20jRcr5so=",
            "Cache-Control": "no-storage",
            "Last-Modified": "Wed, 01 Jan 2020 07:00:00 GMT",
        }
        expected_result = {
            "statusCode": 200,
            "headers": headers,
            "body": '{"name": "foo", "updated_at": "2020-01-01T07:00:00+00:00"}',
        }
        self.assertEqual(expected_result, result)
        # noinspection SpellCheckingInspection
        event["headers"] = {
            "If-Match": "3g6+tMQd4iiW50nY1WFSohCR/S4DGhUbtq20jRcr5so=",
        }
        result = invoker(event, None)
        # noinspection PyTypeChecker
        expected_result = {
            "statusCode": 304,
            "headers": headers,
            "body": "",
        }
        self.assertEqual(expected_result, result)
        # noinspection PyTypeChecker
        event["headers"] = {
            "If-Modified-Since": "Thu, 02 Jan 2020 07:00:00 GMT",
        }
        result = invoker(event, None)
        # noinspection PyTypeChecker,SpellCheckingInspection
        expected_result = {
            "statusCode": 304,
            "headers": {
                "Content-Type": "application/json",
                "Cache-Control": "no-storage",
                "ETag": "3g6+tMQd4iiW50nY1WFSohCR/S4DGhUbtq20jRcr5so=",
                "Last-Modified": result["headers"]["Last-Modified"],
            },
            "body": "",
        }
        self.assertEqual(expected_result, result)

    def test_api_gateway_get_with_path_params(self):
        invoker = get_invoker(get_node_by_path)
        event = dict(httpMethod="GET", pathParameters=dict(name="foo"))
        result = invoker(event, None)
        # noinspection PyTypeChecker
        expected_result = {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
            },
            "body": '{"name": "foo", "child_nodes": []}',
        }
        self.assertEqual(expected_result, result)

    def test_appsync_post_nested(self):
        with patch.dict(
            os.environ,
            {
                "SERVEY_ACTION_MODULE": __name__,
                "SERVEY_ACTION_FUNCTION_NAME": "Node.tree_size",
            },
        ):
            from servey.servey_aws import lambda_invoker

            importlib.reload(lambda_invoker)
            result = lambda_invoker.invoke(
                {"arguments": {}, "source": {"name": "foobar"}}, None
            )
            self.assertEqual(1, result)

    def test_appsync_post_auth(self):
        authorizer = get_default_authorizer()
        token = authorizer.encode(ROOT)
        invoker = get_invoker(get_authorization)
        event = {
            "arguments": {},
            "request": {"headers": {"authorization": f"Bearer {token}"}},
        }
        result = invoker(event, None)
        self.assertEqual(
            {
                "subject_id": None,
                "scopes": ["root"],
                "not_before": None,
                "expire_at": None,
            },
            result,
        )

        event = {
            "arguments": {},
        }
        with self.assertRaises(AuthorizationError):
            invoker(event, None)

    def test_invalid(self):
        invoker = get_invoker(get_node)
        event = {}
        with self.assertRaises(ServeyError):
            invoker(event, None)

    def test_nested(self):
        with patch.dict(
            os.environ,
            {
                "SERVEY_ACTION_MODULE": __name__,
                "SERVEY_ACTION_FUNCTION_NAME": "Node.tree_size",
            },
        ):
            from servey.servey_aws import lambda_invoker

            importlib.reload(lambda_invoker)
            result = lambda_invoker.invoke(
                {"params": {"self": {"name": "foobar"}}}, None
            )
            self.assertEqual(1, result)

    def test_sqs(self):
        invoker = get_invoker(double)
        event = {
            "Records": [
                {"body": "3"},
                {"body": "5"},
            ]
        }
        result = invoker(event, None)
        self.assertEqual([6, 10], result)

    def test_sqs_batched(self):
        invoker = get_invoker(double_batched)
        event = {
            "Records": [
                {"body": "3"},
                {"body": "5"},
            ]
        }
        result = invoker(event, None)
        self.assertEqual([6, 10], result)

    def test_sqs_invalid(self):
        invoker = get_invoker(add)
        event = {
            "Records": [
                {"body": "[1,2]"},
                {"body": "[3,4]"},
            ]
        }
        with self.assertRaises(ServeyError):
            invoker(event, None)


_NODES = {"foo": Node("foo")}


@action(triggers=(WEB_GET,))
def get_node(name: str) -> Optional[Node]:
    return _NODES.get(name)


@action(triggers=(WebTrigger(WebTriggerMethod.GET, "/nodes/{name}"),))
def get_node_by_path(name: str) -> Optional[Node]:
    return _NODES.get(name)


@action(triggers=(WEB_POST,))
def put_node(node: Node) -> bool:
    _NODES[node.name] = node
    return True


@action(triggers=(WEB_POST,), access_control=ScopeAccessControl("root"))
async def get_authorization(
    authorization: Optional[Authorization],
) -> Optional[Authorization]:
    return authorization


def get_invoker(fn: Callable):
    # noinspection PyUnresolvedReferences
    with patch.dict(
        os.environ,
        {
            "SERVEY_ACTION_MODULE": fn.__module__,
            "SERVEY_ACTION_FUNCTION_NAME": fn.__name__,
        },
    ):
        from servey.servey_aws import lambda_invoker

        importlib.reload(lambda_invoker)
        return lambda_invoker.invoke


@dataclass
class StoredItem:
    name: str
    updated_at: datetime = field(default_factory=datetime.now)


# noinspection PyUnusedLocal
@action(triggers=(WEB_GET,), cache_control=TimestampCacheControl())
def get_stored_item(name: str) -> Optional[StoredItem]:
    return StoredItem("foo", datetime.fromisoformat("2020-01-01"))


@action
def double(value: int) -> int:
    return value * 2


def batched_double(values: List[int]) -> List[int]:
    results = [i * 2 for i in values]
    return results


# noinspection PyUnusedLocal
@action(batch_invoker=BatchInvoker(fn=batched_double))
def double_batched(value: int) -> int:
    """Never actually called!"""


# noinspection PyUnusedLocal
@action
def add(a: int, b: int) -> int:
    """Never actually called!"""
