import importlib
import os
from typing import Optional, Callable
from unittest import TestCase
from unittest.mock import patch

from actions import Node
from servey.action.action import action
from servey.trigger.web_trigger import WEB_POST, WEB_GET


class TestLambdaInvoker(TestCase):

    def test_direct(self):
        invoker = get_invoker(get_node)
        event = dict(name='foo')
        result = invoker(event, None)
        expected_result = {'child_nodes': [], 'name': 'foo'}
        self.assertEqual(expected_result, result)

    def test_appsync_get(self):
        invoker = get_invoker(get_node)
        event = dict(info=dict(variables=dict(name='foo')))
        result = invoker(event, None)
        expected_result = {'child_nodes': [], 'name': 'foo'}
        self.assertEqual(expected_result, result)

    def test_appsync_post(self):
        assert False

    def test_api_gateway_get(self):
        assert False


_NODES = {'foo': Node('foo')}


@action(triggers=(WEB_GET,))
def get_node(name: str) -> Optional[Node]:
    return _NODES.get(name)


@action(triggers=(WEB_POST,))
def put_node(node: Node) -> bool:
    _NODES[node.name] = node
    return True


def get_invoker(fn: Callable):
    # noinspection PyUnresolvedReferences
    with patch.dict(os.environ, {
        'SERVEY_ACTION_MODULE': fn.__module__,
        'SERVEY_ACTION_FUNCTION': fn.__name__
    }):
        from servey.servey_aws import lambda_invoker
        importlib.reload(lambda_invoker)
        return lambda_invoker.invoke
