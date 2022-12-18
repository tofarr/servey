from dataclasses import dataclass, field
from typing import List, ForwardRef, Optional
from unittest import TestCase

from servey.action.action import action, get_action
from servey.servey_strawberry.schema_factory import create_schema_factory
from servey.trigger.web_trigger import WEB_GET, WEB_POST


class TestEntityFactory(TestCase):
    def test_get_input(self):
        schema_factory = create_schema_factory()
        schema_factory.create_field_for_action(get_action(get_node), WEB_GET)
        schema_factory.create_field_for_action(get_action(put_node), WEB_POST)
        schema = schema_factory.create_schema()
        str_schema = str(schema).strip()
        expected_schema = """
type Mutation {
  putNode(path: String!, node: NodeInput!): Boolean!
}

type Node {
  name: String!
  childNodes: [Node!]!
}

input NodeInput {
  name: String!
  childNodes: [NodeInput!]!
}

type Query {
  getNode(path: String! = ""): Node
}
        """.strip()
        self.assertEqual(expected_schema, str_schema)
        result = schema.execute_sync(
            """
query{
  getNode(path: "child_a") {
    name
    childNodes {
      name
    }
  }
}
        """
        )
        expected_result = {
            "getNode": {"name": "child_a", "childNodes": [{"name": "grandchild_a"}]}
        }
        self.assertEqual(expected_result, result.data)
        self.assertIsNone(get_node('foo"'))


@dataclass
class Node:
    name: str
    child_nodes: List[ForwardRef(f"{__name__}.Node")] = field(default_factory=list)


_ROOT = Node("root", [Node("child_a", [Node("grandchild_a")]), Node("child_b")])


@action(triggers=(WEB_GET,))
def get_node(path: str = "") -> Optional[Node]:
    node = _ROOT
    if path:
        path = path.split("/")
        for p in path:
            if p:
                node = next((n for n in node.child_nodes if n.name == p), None)
                if not node:
                    return None
    return node


# noinspection PyUnusedLocal
@action(triggers=(WEB_POST,))
def put_node(path: str, node: Node) -> bool:
    """Not actually invoked, so do noop"""
