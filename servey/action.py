import inspect
from dataclasses import dataclass
from typing import Dict, Callable, Optional, Tuple

from marshy import get_default_context
from marshy.marshaller.marshaller_abc import MarshallerABC
from marshy.marshaller.obj_marshaller import ObjMarshaller, attr_config
from marshy.marshaller_context import MarshallerContext
from schemey.object_schema import ObjectSchema
from schemey.property_schema import PropertySchema
from schemey.schema_abc import SchemaABC
from schemey.schema_context import SchemaContext, get_default_schema_context

from servey.authorizer.authorizer_abc import AuthorizerABC
from servey.authorizer.no_authorizer import NoAuthorizer
from servey.cache.cache_control_abc import CacheControlABC
from servey.cache.no_cache_control import NoCacheControl
from servey.graphql_type import GraphqlType
from servey.http_method import HttpMethod
from servey.meta.action_meta import ActionMeta

_empty = inspect.Signature.empty


@dataclass(frozen=True)
class Action:
    name: str
    doc: Optional[str]
    callable: Callable
    params_marshaller: ObjMarshaller
    return_marshaller: MarshallerABC
    params_schema: ObjectSchema[Dict]
    return_schema: SchemaABC
    authorizer: AuthorizerABC
    path: str
    http_methods: Tuple[HttpMethod, ...] = (HttpMethod.GET,)
    graphql_type: GraphqlType = GraphqlType.QUERY
    cache_control: CacheControlABC = NoCacheControl()  # Mostly used for https based transport medium

    def get_meta(self) -> ActionMeta:
        return ActionMeta(self.name, self.doc, self.params_schema, self.return_schema, self.authorizer,
                          list(self.http_methods), self.graphql_type, self.cache_control)


def action(callable_: Callable,
           name: Optional[str] = None,
           marshaller_context: Optional[MarshallerContext] = None,
           schema_context: Optional[SchemaContext] = None,
           path: Optional[str] = None,
           http_methods: Tuple[HttpMethod, ...] = (HttpMethod.POST,),
           graphql_type: Optional[GraphqlType] = None,
           cache_control: CacheControlABC = NoCacheControl(),
           authorizer: AuthorizerABC = NoAuthorizer()  # Not sure if this should be the default
           ) -> Action:
    if name is None:
        name = callable_.__name__
    if path is None:
        path = '/'+name.replace('_', '-')
    params_schema = build_params_schema(callable_, schema_context)
    if graphql_type is None:
        if http_methods == (HttpMethod.GET,):
            graphql_type = GraphqlType.QUERY
        else:
            graphql_type = GraphqlType.MUTATION
    doc = None
    if callable_.__doc__:
        doc = ' '.join(callable_.__doc__.split())
    action_ = Action(
        callable=callable_,
        name=name,
        doc=doc,
        params_marshaller=build_params_marshaller(callable_, marshaller_context),
        return_marshaller=build_return_marshaller(callable_, marshaller_context),
        params_schema=build_params_schema(callable_, schema_context),
        return_schema=build_return_schema(callable_, schema_context),
        cache_control=cache_control,
        path=path,
        http_methods=http_methods,
        graphql_type=graphql_type,
        authorizer=authorizer
    )
    return action_


def build_params_marshaller(callable_: Callable,
                            marshaller_context: Optional[MarshallerContext] = None,
                            offset: int = 0
                            ) -> ObjMarshaller[Dict]:
    if marshaller_context is None:
        marshaller_context = get_default_context()
    sig = inspect.signature(callable_)
    params_marshaller = ObjMarshaller[Dict](dict, tuple(
        attr_config(marshaller_context.get_marshaller(p.annotation), p.name)
        for p in list(sig.parameters.values())[offset:]
    ))
    return params_marshaller


def build_return_marshaller(callable_: Callable,
                            marshaller_context: Optional[MarshallerContext] = None
                            ) -> MarshallerABC:
    if marshaller_context is None:
        marshaller_context = get_default_context()
    sig = inspect.signature(callable_)
    if sig.return_annotation is inspect.Parameter.empty:
        raise ValueError(f'no_return_annotation_for_method:{callable_.__name__}')
    return_marshaller = marshaller_context.get_marshaller(sig.return_annotation)
    return return_marshaller


def build_params_schema(callable_: Callable,
                        schema_context: Optional[SchemaContext] = None,
                        offset: int = 0
                        ) -> ObjectSchema[Dict]:
    if schema_context is None:
        schema_context = get_default_schema_context()
    sig = inspect.signature(callable_)
    params_schema = ObjectSchema(dict, tuple(
        PropertySchema(
            name=p.name,
            schema=schema_context.get_schema(p.annotation, None if p.default is _empty else p.default),
            required=p.default is _empty)
        for p in list(sig.parameters.values())[offset:]
    ))
    return params_schema


def build_return_schema(callable_: Callable,
                        schema_context: Optional[SchemaContext] = None
                        ) -> SchemaABC:
    if schema_context is None:
        schema_context = get_default_schema_context()
    sig = inspect.signature(callable_)
    return_schema = schema_context.get_schema(sig.return_annotation)
    return return_schema
