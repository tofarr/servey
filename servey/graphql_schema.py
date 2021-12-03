from dataclasses import dataclass, field
from io import StringIO
from typing import Dict, Optional, TextIO

from schemey.any_of_schema import AnyOfSchema
from schemey.enum_schema import EnumSchema
from schemey.graphql.graphql_object_type import GraphqlObjectType
from schemey.graphql_context import GraphqlContext
from schemey.object_schema import ObjectSchema

from servey.handler.action_handler import ActionHandler
from servey.handler.action_type import ActionType
from servey.handler.app_handler import AppHandler


@dataclass
class GraphqlSchema:
    inputs: Dict[str, ObjectSchema] = field(default_factory=dict)
    types: Dict[str, ObjectSchema] = field(default_factory=dict)
    enums: Dict[str, EnumSchema] = field(default_factory=dict)
    unions: Dict[str, AnyOfSchema] = field(default_factory=dict)
    actions: Dict[str, ActionHandler] = field(default_factory=dict)

    def add_actions(self, app_handler: AppHandler):
        for handler in app_handler.handlers:
            if isinstance(handler, ActionHandler):
                self.add_action(handler)

    def add_action(self, action: ActionHandler):
        self.actions[action.name] = action
        input_context = GraphqlContext(GraphqlObjectType.INPUT, self.inputs, self.enums, self.unions)
        for property_schema in action.params_schema.property_schemas:
            property_schema.schema.to_graphql_schema(input_context)
        type_context = GraphqlContext(GraphqlObjectType.TYPE, self.types, self.enums, self.unions)
        action.return_schema.to_graphql_schema(type_context)

    def to_graphql_schema(self, writer: Optional[TextIO] = None) -> Optional[str]:
        local_writer = writer or StringIO()
        for enum in self.enums.values():
            enum.to_graphql(local_writer)
        for input_ in self.inputs.values():
            input_.to_graphql(local_writer, GraphqlObjectType.INPUT)
        for type_ in self.types.values():
            type_.to_graphql(local_writer, GraphqlObjectType.TYPE)
        action_types = []
        for action_type in ActionType:
            if self._actions_to_graphql_schema(action_type, local_writer):
                action_types.append(action_type)
        local_writer.write('\n\nschema {\n')
        for action_type in action_types:
            local_writer.write(f'\t{action_type.value}: {action_type.value.title()}\n')
        local_writer.write('}\n\n')
        if writer is None:
            return local_writer.read()

    def _actions_to_graphql_schema(self, action_type: ActionType, writer: TextIO) -> bool:
        actions = [a for a in self.actions.values() if a.action_type == action_type]
        if not actions:
            return False
        writer.write('type %s {\n\n' % action_type.value.title())
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
