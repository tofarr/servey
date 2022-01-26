from dataclasses import dataclass
from typing import Optional

from marshy import ExternalType
from marshy.marshaller.marshaller_abc import MarshallerABC
from marshy.marshaller_context import MarshallerContext
from schemey.any_of_schema import optional_schema
from schemey.object_schema import ObjectSchema
from schemey.property_schema import PropertySchema
from schemey.schema_abc import SchemaABC
from schemey.schema_context import SchemaContext
from schemey.string_schema import StringSchema


@dataclass
class PublisherMeta:
    name: str
    doc: Optional[str]
    event_schema: SchemaABC

    # noinspection PyUnusedLocal
    @classmethod
    def __marshaller_factory__(cls, context: MarshallerContext):
        return _PublisherMetaMarshaller(PublisherMeta)

    # noinspection PyUnusedLocal
    @classmethod
    def __schema_factory__(cls, default_value, context: SchemaContext):
        # custom schema that keeps things vague around params and return as there is no schema for a schema (yet)
        return ObjectSchema(PublisherMeta, (
            PropertySchema('name', StringSchema()),
            PropertySchema('doc', optional_schema(StringSchema())),
            PropertySchema('event_schema', ObjectSchema(SchemaABC, additional_properties=True, name='EventSchema')),
        ), default_value=default_value)


class _PublisherMetaMarshaller(MarshallerABC):

    def load(self, item: ExternalType) -> PublisherMeta:
        raise NotImplementedError()

    def dump(self, item: PublisherMeta) -> ExternalType:
        dumped = dict(name=item.name)
        if item.doc:
            dumped['doc'] = item.doc
        dumped['event_schema'] = item.event_schema.to_json_schema()
        return dumped
