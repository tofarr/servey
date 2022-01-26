from dataclasses import dataclass
from typing import Optional, Dict, Iterator, List, Tuple

from marshy import ExternalType
from marshy.marshaller.marshaller_abc import MarshallerABC, T
from marshy.marshaller_context import MarshallerContext
from schemey.any_of_schema import optional_schema
from schemey.deferred_schema import DeferredSchema
from schemey.object_schema import ObjectSchema
from schemey.property_schema import PropertySchema
from schemey.schema_abc import SchemaABC
from schemey.schema_context import SchemaContext
from schemey.string_schema import StringSchema

from servey.authorizer.authorizer_abc import AuthorizerABC
from servey.cache.cache_control_abc import CacheControlABC
from servey.cache.no_cache_control import NoCacheControl
from servey.graphql_type import GraphqlType
from servey.http_method import HttpMethod


@dataclass
class ActionMeta:
    name: str
    doc: Optional[str]
    params_schema: ObjectSchema[Dict]
    return_schema: SchemaABC
    authorizer: AuthorizerABC
    http_methods: List[HttpMethod]
    graphql_type: GraphqlType
    cache_control: CacheControlABC = NoCacheControl()  # Mostly used for https based transport medium

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
            PropertySchema('authorizer', DeferredSchema(context, AuthorizerABC)),
            PropertySchema('http_methods', context.get_schema(List[HttpMethod])),
            PropertySchema('graphql_type', context.get_schema(GraphqlType)),
            PropertySchema('cache_control', DeferredSchema(context, CacheControlABC)),
        ), default_value=default_value)


class _ActionMetaMarshaller(MarshallerABC[ActionMeta]):

    def load(self, item: ExternalType) -> ActionMeta:
        raise NotImplementedError()

    def dump(self, item: ActionMeta) -> ExternalType:
        dumped = dict(name=item.name)
        if item.doc:
            dumped['doc'] = item.doc
        dumped['params_schema'] = item.params_schema.to_json_schema()
        dumped['return_schema'] = item.return_schema.to_json_schema()
        return dumped
