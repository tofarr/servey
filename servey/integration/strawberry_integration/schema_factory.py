from dataclasses import dataclass, field, fields, is_dataclass
from inspect import Signature
from typing import Type, Dict, List, Set, Optional, Tuple

import strawberry
import typing_inspect
from marshy.factory.impl_marshaller_factory import get_impls
from marshy.factory.optional_marshaller_factory import get_optional_type
from strawberry.annotation import StrawberryAnnotation

# noinspection PyProtectedMember
from strawberry.field import StrawberryField, UNRESOLVED
from strawberry.type import StrawberryOptional, StrawberryContainer
from strawberry.types.fields.resolver import StrawberryResolver

from servey.action import Action
from servey.action_context import get_default_action_context, ActionContext
from servey.integration.strawberry_integration.entity_factory.entity_factory_abc import (
    EntityFactoryABC,
)
from servey.integration.strawberry_integration.injector.injector_abc import InjectorABC
from servey.integration.strawberry_integration.injector.injector_factory_abc import (
    InjectorFactoryABC,
)
from servey.trigger.web_trigger import WebTrigger, UPDATE_METHODS


@dataclass
class SchemaFactory:
    types: Dict[str, Type] = field(default_factory=dict)
    inputs: Dict[str, Type] = field(default_factory=dict)
    enums: Dict[str, Type] = field(default_factory=dict)
    query: Dict[str, StrawberryField] = field(default_factory=dict)
    mutation: Dict[str, StrawberryField] = field(default_factory=dict)
    entity_factories: List[EntityFactoryABC] = field(default_factory=list)
    injector_factories: List[InjectorFactoryABC] = field(default_factory=list)

    def create_input(self, annotation: Type) -> Type:
        for entity_factory in self.entity_factories:
            i = entity_factory.create_input(annotation, self)
            if i:
                return i

    def create_type(self, annotation: Type):
        for entity_factory in self.entity_factories:
            type_ = entity_factory.create_input(annotation, self)
            if type_:
                return type_

    def add_fields(self, action_context: Optional[ActionContext] = None):
        if not action_context:
            action_context = get_default_action_context()
        for action, trigger in action_context.get_actions_with_trigger_type(WebTrigger):
            self.create_field_for_action(action, trigger)

    def create_field_for_action(self, action: Action, trigger: WebTrigger):
        sig, injectors = self.create_signature(action)

        def resolver(**kwargs):
            executor = action.create_executor()
            to_exclude = set()
            for injector in injectors:
                injector.inject(executor, kwargs, to_exclude)
            for key in to_exclude:
                kwargs.pop(key, None)
            result = executor.execute(**kwargs)
            # TODO: Convert result to strawberry type
            return result

        resolver.__signature__ = sig
        f = strawberry.field(resolver=resolver)
        f.name = action.action_meta.name
        if trigger.method in UPDATE_METHODS:
            self.mutation[f.name] = f
        else:
            self.query[f.name] = f

    def create_signature(self, action: Action) -> Tuple[Signature, List[InjectorABC]]:
        sig = action.get_signature()
        parameters = []
        for param in sig.parameters.values():
            parameters.append(
                param.replace(annotation=self.create_input(param.annotation))
            )
        injectors = []
        for injector_factory in self.injector_factories:
            injector = injector_factory.create_injector(action, parameters)
            if injector:
                injectors.append(injector)
        return_annotation = self.create_type(sig.return_annotation)
        sig = sig.replace(parameters=parameters, return_annotation=return_annotation)
        return sig, injectors

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
        queries = strawberry.type(type("Query", (), query_params))

        mutation_params = {
            **self.mutation,
            "__annotations__": {f.name: f.type for f in self.mutation.values()},
        }
        mutations = strawberry.type(type("Mutation", (), mutation_params))

        schema = strawberry.Schema(queries, mutations)
        return schema


def new_schema_for_context(action_context: Optional[ActionContext] = None):
    if not action_context:
        action_context = get_default_action_context()
    entity_factories = [f() for f in get_impls(EntityFactoryABC)]
    entity_factories.sort(key=lambda f: f.priority, reverse=True)
    injector_factories = [f() for f in get_impls(InjectorFactoryABC)]
    injector_factories.sort(key=lambda f: f.priority, reverse=True)
    schema_factory = SchemaFactory(
        entity_factories=entity_factories, injector_factories=injector_factories
    )
    for action, trigger in action_context.get_actions_with_trigger_type(WebTrigger):
        schema_factory.create_field_for_action(action, trigger)
    schema = schema_factory.create_schema()
    return schema
