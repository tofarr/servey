from dataclasses import dataclass, field
from io import StringIO
from typing import Dict, Optional, TextIO, List

import Subscription as Subscription
from schemey.any_of_schema import AnyOfSchema
from schemey.enum_schema import EnumSchema
from schemey.graphql.graphql_object_type import GraphqlObjectType
from schemey.graphql_context import GraphqlContext
from schemey.object_schema import ObjectSchema

from servey import Action
from servey import ActionType
from servey import ServeyContext, get_default_servey_context


@dataclass
class GraphqlSchema:
    inputs: Dict[str, ObjectSchema] = field(default_factory=dict)
    types: Dict[str, ObjectSchema] = field(default_factory=dict)
    enums: Dict[str, EnumSchema] = field(default_factory=dict)
    unions: Dict[str, AnyOfSchema] = field(default_factory=dict)
    queries: Dict[str, Action] = field(default_factory=dict)
    mutations: Dict[str, Action] = field(default_factory=dict)
    subscriptions: Dict[str, Subscription] = field(default_factory=dict)

    def add_action(self, action: Action):
        actions = self.queries if action.action_type in (ActionType.GET, ActionType.HEAD) else self.mutations
        actions[action.name] = action
        input_context = GraphqlContext(GraphqlObjectType.INPUT, self.inputs, self.enums, self.unions)
        for property_schema in action.params_schema.property_schemas:
            property_schema.schema.to_graphql_schema(input_context)
        type_context = GraphqlContext(GraphqlObjectType.TYPE, self.types, self.enums, self.unions)
        action.return_schema.to_graphql_schema(type_context)

    def to_graphql(self, writer: Optional[TextIO] = None) -> Optional[str]:
        local_writer = writer or StringIO()
        for enum in self.enums.values():
            enum.to_graphql(local_writer)
        for input_ in self.inputs.values():
            input_.to_graphql(local_writer, GraphqlObjectType.INPUT)
        for type_ in self.types.values():
            type_.to_graphql(local_writer, GraphqlObjectType.TYPE)
        queries = self._actions_to_graphql_schema('Queries', list(self.queries.values()), local_writer)
        mutations = self._actions_to_graphql_schema('Mutations', list(self.mutations.values()), local_writer)
        subscriptions = False
        local_writer.write('\n\nschema {\n')
        if queries:
            local_writer.write('\tqueries: Queries\n')
        if mutations:
            local_writer.write('\tmutations: Mutations\n')
        if subscriptions:
            local_writer.write('\tsubscriptions: Subscriptions\n')
        local_writer.write('}\n\n')
        if writer is None:
            return local_writer.read()

    @staticmethod
    def _actions_to_graphql_schema(category: str, actions: List[Action], writer: TextIO) -> bool:
        if not actions:
            return False
        writer.write('type %s {\n\n' % category)
        for action in actions:
            if action.doc:
                writer.write('"""\n%s\n"""\n' % action.doc.replace("\n", "\n\t"))
            writer.write(f'\t{action.name}')
            if action.params_schema.property_schemas:
                writer.write('(\n')
                for property_schema in action.params_schema.property_schemas:
                    writer.write('\t')
                    property_schema.to_graphql(writer)
                writer.write('t\n)')
            writer.write('\n\n')
        writer.write('}\n\n')
        return True


def graphql_schema(context: Optional[ServeyContext] = None) -> GraphqlSchema:
    if context is None:
        context = get_default_servey_context()
    schema = GraphqlSchema()
    for action in context.actions_by_name.values():
        schema.add_action(action)
    return schema
