from dataclasses import dataclass
from typing import Optional, Dict, Any

from marshy import ExternalType
from marshy.marshaller.marshaller_abc import MarshallerABC, T
from marshy.marshaller_context import MarshallerContext
from schemey.any_of_schema import optional_schema, AnyOfSchema
from schemey.object_schema import ObjectSchema
from schemey.property_schema import PropertySchema
from schemey.schema_abc import SchemaABC
from schemey.schema_context import SchemaContext
from schemey.string_schema import StringSchema


@dataclass
class ActionMeta:
    name: str
    doc: Optional[str] = None
    params_schema: ObjectSchema[Dict[str, Any]] = None
    return_schema: SchemaABC = None

    # noinspection PyUnusedLocal
    @classmethod
    def __marshaller_factory__(cls, context: MarshallerContext):
        return _ActionMetaMarshaller(ActionMeta)

    # noinspection PyUnusedLocal
    @classmethod
    def __schema_factory__(cls, default_value, context: SchemaContext):
        # custom schema that keeps things vague around params and return as there is no schema for a schema (yet)
        return ObjectSchema(ActionMeta, (
            PropertySchema('name', StringSchema()),
            PropertySchema('doc', optional_schema(StringSchema())),
            PropertySchema('params_schema', ObjectSchema(SchemaABC, additional_properties=True, name='ParamsSchema')),
            PropertySchema('return_schema', ObjectSchema(SchemaABC, additional_properties=True, name='ReturnSchema')),
        ), default_value=default_value)


class _ActionMetaMarshaller(MarshallerABC):

    def load(self, item: ExternalType) -> T:
        raise NotImplementedError()

    def dump(self, item: T) -> ExternalType:
        dumped = dict(name=item.name)
        if item.doc:
            dumped['doc'] = item.doc
        dumped['params_schema'] = item.params_schema.to_json_schema()
        dumped['return_schema'] = item.return_schema.to_json_schema()
        return dumped
