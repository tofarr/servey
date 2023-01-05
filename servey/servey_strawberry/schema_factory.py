import logging
from dataclasses import dataclass, field, fields, is_dataclass
from typing import Type, Dict, List, Set

import strawberry
import typing_inspect
from marshy.factory.impl_marshaller_factory import get_impls
from marshy.factory.optional_marshaller_factory import get_optional_type
from strawberry.annotation import StrawberryAnnotation

# noinspection PyProtectedMember
from strawberry.field import StrawberryField, UNRESOLVED
from strawberry.type import StrawberryOptional, StrawberryContainer
from strawberry.types.fields.resolver import StrawberryResolver

from servey.action.action import Action
from servey.finder.action_finder_abc import find_actions_with_trigger_type
from servey.trigger.web_trigger import WebTrigger, UPDATE_METHODS
from servey.servey_strawberry.entity_factory.entity_factory_abc import (
    EntityFactoryABC,
)
from servey.servey_strawberry.handler_filter.handler_filter_abc import (
    HandlerFilterABC,
)

LOGGER = logging.getLogger(__name__)


@dataclass
class SchemaFactory:
    """
    This class is tasked with converting standard python types into types usable by strawberry and therefore graphql.
    """

    types: Dict[str, Type] = field(default_factory=dict)
    inputs: Dict[str, Type] = field(default_factory=dict)
    enums: Dict[str, Type] = field(default_factory=dict)
    query: Dict[str, StrawberryField] = field(default_factory=dict)
    mutation: Dict[str, StrawberryField] = field(default_factory=dict)
    subscription: Dict[str, StrawberryField] = field(default_factory=dict)
    entity_factories: List[EntityFactoryABC] = field(default_factory=list)
    handler_filters: List[HandlerFilterABC] = field(default_factory=list)

    def get_input(self, annotation: Type) -> Type:
        if hasattr(annotation, "__name__"):
            i = self.inputs.get(annotation.__name__)
            if i:
                return i
        for entity_factory in self.entity_factories:
            i = entity_factory.create_input(annotation, self)
            if i:
                if hasattr(annotation, "__name__"):
                    self.inputs[annotation.__name__] = i
                return i

    def get_type(self, annotation: Type):
        if hasattr(annotation, "__name__"):
            type_ = self.types.get(annotation.__name__)
            if type_:
                return type_
        for entity_factory in self.entity_factories:
            type_ = entity_factory.create_type(annotation, self)
            if type_:
                if hasattr(annotation, "__name__"):
                    self.types[annotation.__name__] = type_
                return type_

    def create_field_for_action(self, action: Action, trigger: WebTrigger):
        for handler_filter in self.handler_filters:
            action, continue_filtering = handler_filter.filter(action, self)
            if not continue_filtering:
                break

        f = strawberry.field(resolver=action.fn)
        f.name = action.name
        if trigger.method in UPDATE_METHODS:
            self.mutation[f.name] = f
        else:
            self.query[f.name] = f

    def _resolve_type_futures(self, type_, resolved: Set):
        if isinstance(type_, str):
            type_ = self.types[type_]
        if isinstance(type_, StrawberryAnnotation):
            type_.type = self._resolve_type_futures(type_.annotation, resolved)
            return type_
        if isinstance(type_, StrawberryContainer):
            type_.of_type = self._resolve_type_futures(type_.of_type, resolved)
            return type_
        name = typing_inspect.get_forward_arg(type_)
        if name:
            type_ = self.types[name]
            return type_
        optional_type = get_optional_type(type_)
        if optional_type:
            return StrawberryOptional(
                self._resolve_type_futures(optional_type, resolved)
            )
        origin = typing_inspect.get_origin(type_)
        if origin:
            args = tuple(
                self._resolve_type_futures(a, resolved)
                for a in typing_inspect.get_args(type_)
            )
            if origin is list:
                return List[args]
            else:
                return origin[args]
        if is_dataclass(type_):
            if type_.__name__ in resolved:
                return type_
            resolved.add(type_.__name__)
            # noinspection PyDataclass
            for f in fields(type_):
                if isinstance(f, StrawberryField):
                    if f.type is UNRESOLVED:
                        resolver = f.base_resolver
                        field_type = resolver.signature.return_annotation
                        field_type = self._resolve_type_futures(field_type, resolved)
                        resolver_override = StrawberryResolver(
                            resolver.wrapped_func, type_override=field_type
                        )
                        f.base_resolver = resolver_override
                else:
                    f.type = self._resolve_type_futures(f.type, resolved)
        return type_

    def create_schema(self):
        resolved = set()
        for f in self.query.values():
            f.type = self._resolve_type_futures(f.type, resolved)
        for f in self.mutation.values():
            f.type = self._resolve_type_futures(f.type, resolved)

        query_params = {
            **self.query,
            "__annotations__": {f.name: f.type for f in self.query.values()},
        }
        queries = (
            strawberry.type(type("Query", (), query_params)) if self.query else None
        )

        mutation_params = {
            **self.mutation,
            "__annotations__": {f.name: f.type for f in self.mutation.values()},
        }
        mutations = (
            strawberry.type(type("Mutation", (), mutation_params))
            if self.mutation
            else None
        )

        subscription_params = {
            **self.subscription,
            "__annotations__": {s.name: s.type for s in self.subscription.values()},
        }
        subscriptions = (
            strawberry.type(type("Subscription", (), subscription_params))
            if self.subscription
            else None
        )

        if not queries:
            LOGGER.warning("No graphql queries found - skipping schema generation")
            return None  # strawberry requires an API has at least 1 query!
        schema = strawberry.Schema(queries, mutations, subscriptions)
        return schema


def create_schema_factory() -> SchemaFactory:
    entity_factories = [f() for f in get_impls(EntityFactoryABC)]
    entity_factories.sort(key=lambda f: f.priority, reverse=True)
    handler_filters = [f() for f in get_impls(HandlerFilterABC)]
    handler_filters.sort(key=lambda f: f.priority, reverse=True)
    schema_factory = SchemaFactory(
        entity_factories=entity_factories, handler_filters=handler_filters
    )
    return schema_factory


def create_schema():
    schema_factory = create_schema_factory()
    for action, trigger in find_actions_with_trigger_type(WebTrigger):
        schema_factory.create_field_for_action(action, trigger)
    schema = schema_factory.create_schema()
    return schema
