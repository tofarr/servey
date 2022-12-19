import dataclasses
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, ForwardRef, Optional, Tuple, Set
from unittest import TestCase

import strawberry
from strawberry.annotation import StrawberryAnnotation
from strawberry.field import StrawberryField, UNRESOLVED
from strawberry.type import StrawberryOptional

from servey.action.action import action, get_action, Action
from servey.action.resolvable import resolvable
from servey.servey_strawberry.handler_filter.handler_filter_abc import HandlerFilterABC
from servey.servey_strawberry.schema_factory import create_schema_factory, SchemaFactory
from servey.trigger.web_trigger import WEB_GET, WEB_POST


class TestEntityFactory(TestCase):
    def test_get_input(self):
        schema_factory = create_schema_factory()
        schema_factory.create_field_for_action(get_action(get_node), WEB_GET)
        schema_factory.create_field_for_action(get_action(get_node_by_name), WEB_GET)
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
  treeSize: Int!
}

input NodeInput {
  name: String!
  childNodes: [NodeInput!]!
}

type Query {
  getNode(path: String! = ""): Node
  getNodeByName(name: String! = ""): Node
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
        self.assertIsNone(get_node_by_name('foo'))
        self.assertEqual(
            Node(name='child_a', child_nodes=[
                Node(name='grandchild_a', child_nodes=[])
            ]),
            get_node_by_name('child_a')
        )
        self.assertIs(schema_factory.get_type(Node), schema_factory.get_type(Node))

    def test_handler_filter_stopper(self):

        def static_tree_size():
            return 10

        class StopHandlerFilter(HandlerFilterABC):
            def filter(self, action_: Action, schema_factory_: SchemaFactory) -> Tuple[Action, bool]:
                if action_.name == "tree_size":
                    action_ = dataclasses.replace(action_, fn=static_tree_size)
                    return action_, False
                return action_, True

        schema_factory = create_schema_factory()
        schema_factory.handler_filters.append(StopHandlerFilter())
        schema_factory.create_field_for_action(get_action(get_node), WEB_GET)
        schema_factory.create_field_for_action(get_action(get_node_by_name), WEB_GET)
        schema_factory.create_field_for_action(get_action(put_node), WEB_POST)
        schema = schema_factory.create_schema()
        result = schema.execute_sync("""
            query{
                getNodeByName(name: "grandchild_a") {
                    name
                    treeSize
                }
            }
        """)
        expected_result = {
            "getNodeByName": {"name": "grandchild_a", "treeSize": 10}
        }
        self.assertEqual(expected_result, result.data)

    def test_tree_size(self):
        self.assertEqual(4, _ROOT.tree_size())

    def test_create_field_for_action(self):
        class DummyHandlerFilter(HandlerFilterABC):
            def filter(
                    self,
                    action: Action,
                    schema_factory: SchemaFactory
            ) -> Tuple[Action, bool]:
                return action, False

        @strawberry.type
        class Cat:
            name: str

        @strawberry.type
        class Dog:
            name: str

        @strawberry.type
        class Owner:
            name: str
            pet: strawberry.union("Pet", types=(Cat, Dog))

        @action(triggers=(WEB_GET,))
        def dummy() -> Owner:
            """ Dummy """

        schema_factory = create_schema_factory()
        schema_factory.handler_filters.append(DummyHandlerFilter())
        schema_factory.create_field_for_action(get_action(dummy), WEB_GET)
        schema = schema_factory.create_schema()

    def test_resolve_type_futures_str(self):
        schema_factory = create_schema_factory()
        # noinspection PyTypeChecker
        schema_factory.types['Foo'] = 'bar'
        self.assertEqual('bar', schema_factory._resolve_type_futures('Foo', set()))

    def test_resolve_type_futures_strawberry_annotation(self):
        schema_factory = create_schema_factory()
        # noinspection PyTypeChecker
        schema_factory.types['str'] = 'bar'
        # noinspection PyTypeChecker
        annotation = StrawberryAnnotation("str")
        resolved_type = schema_factory._resolve_type_futures(annotation, set())
        self.assertEqual(annotation, resolved_type)

    def test_resolve_type_futures_forward_ref(self):
        schema_factory = create_schema_factory()
        # noinspection PyTypeChecker
        schema_factory.types['int'] = 'bar'
        # noinspection PyTypeChecker
        annotation = ForwardRef("int")
        resolved_type = schema_factory._resolve_type_futures(annotation, set())
        self.assertEqual('bar', resolved_type)

    def test_resolve_type_futures_strawberry_optional(self):
        schema_factory = create_schema_factory()
        # noinspection PyTypeChecker
        schema_factory.types['str'] = 'bar'
        # noinspection PyTypeChecker
        annotation = StrawberryOptional(Optional[int])
        resolved_type = schema_factory._resolve_type_futures(annotation, set())
        self.assertEqual(annotation, resolved_type)

    def test_resolve_type_futures_strawberry_set(self):
        schema_factory = create_schema_factory()
        # noinspection PyTypeChecker
        schema_factory.types['str'] = 'bar'
        # noinspection PyTypeChecker
        annotation = Set[int]
        resolved_type = schema_factory._resolve_type_futures(annotation, set())
        self.assertEqual(set[int], resolved_type)

    def test_resolve_type_futures_dataclass(self):
        schema_factory = create_schema_factory()

        def another_now() -> UNRESOLVED:
            return datetime.now()

        @strawberry.type
        class Times:
            also_now = strawberry.field(resolver=another_now)

            @strawberry.field
            def now(self) -> datetime:
                return datetime.now()

        # noinspection PyTypeChecker
        resolved_type = schema_factory._resolve_type_futures(Times, set())
        self.assertEqual(Times, resolved_type)


@dataclass
class Node:
    name: str
    child_nodes: List[ForwardRef(f"{__name__}.Node")] = field(default_factory=list)

    @resolvable
    def tree_size(self) -> int:
        result = 1 + sum(n.tree_size() for n in self.child_nodes)
        return result

    def get_node_by_name(self, name: str) -> Optional["Node"]:
        if name == self.name:
            return self
        for c in self.child_nodes:
            node = c.get_node_by_name(name)
            if node:
                return node

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


@action(triggers=(WEB_GET,))
def get_node_by_name(name: str = "") -> Optional[Node]:
    node = _ROOT.get_node_by_name(name)
    return node


# noinspection PyUnusedLocal
@action(triggers=(WEB_POST,))
def put_node(path: str, node: Node) -> bool:
    """Not actually invoked, so do noop"""