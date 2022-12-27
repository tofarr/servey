import inspect
from dataclasses import is_dataclass, fields, dataclass
from typing import Type, Optional, Dict, Any

import strawberry
from strawberry.dataloader import DataLoader

from servey.action.action import Action
from servey.action.resolvable import Resolvable, get_resolvable
from servey.servey_strawberry.entity_factory.entity_factory_abc import (
    EntityFactoryABC,
)
from servey.servey_strawberry.schema_factory import SchemaFactory
from servey.servey_strawberry.schema_factory_lazy_input import SchemaFactoryLazyInput
from servey.servey_strawberry.schema_factory_lazy_type import SchemaFactoryLazyType


class DataclassFactory(EntityFactoryABC):
    priority: int = 120

    def create_type(
        self, annotation: Type, schema_factory: SchemaFactory
    ) -> Optional[Type]:
        if not is_dataclass(annotation):
            return
        # noinspection PyTypeChecker
        schema_factory.types[annotation.__name__] = SchemaFactoryLazyType(
            type_name=annotation.__name__, module="", schema_factory=schema_factory
        )

        annotations = {}
        params = {"__annotations__": annotations}
        # noinspection PyDataclass
        for f in fields(annotation):
            annotations[f.name] = schema_factory.get_type(f.type)

        # Check for functions decorated with @resolvable
        for key, value in annotation.__dict__.items():
            resolvable = get_resolvable(value)
            if resolvable:
                build_resolvable_field(resolvable, schema_factory, key, params)

        wrap_type = type(annotation.__name__, tuple(), params)
        type_ = strawberry.type(wrap_type)
        schema_factory.types[annotation.__name__] = type_
        # noinspection PyDataclass
        for field in fields(type_):
            field.type = schema_factory.get_type(field.type)
        return type_

    def create_input(
        self, annotation: Type, schema_factory: SchemaFactory
    ) -> Optional[Type]:
        if not is_dataclass(annotation):
            return
        name = f"{annotation.__name__}Input"
        input_ = schema_factory.inputs.get(name)
        if input_:
            return input_
        # noinspection PyTypeChecker
        schema_factory.inputs[name] = SchemaFactoryLazyInput(
            type_name=name, module="", schema_factory=schema_factory
        )

        # noinspection PyDataclass
        params = {
            "__annotations__": {
                f.name: schema_factory.get_input(f.type) for f in fields(annotation)
            },
        }
        wrap_type = dataclass(type(name, tuple(), params))
        input_ = strawberry.input(wrap_type)
        schema_factory.inputs[name] = input_
        # noinspection PyDataclass
        for field in fields(input_):
            field.type = schema_factory.get_input(field.type)
        return input_


def build_resolvable_field(
    resolvable: Resolvable,
    schema_factory: SchemaFactory,
    key: str,
    params: Dict[str, Any],
):
    if resolvable.batch_fn:
        fn = _wrap_fn_in_data_loader(resolvable)
    else:
        fn = resolvable.fn

    action = Action(
        name=key,
        fn=fn,
        access_control=resolvable.access_control,
        cache_control=resolvable.cache_control,
    )

    for handler_filter in schema_factory.handler_filters:
        action, continue_filtering = handler_filter.filter(action, schema_factory)
        if not continue_filtering:
            break

    sig = inspect.signature(fn)
    return_type = schema_factory.get_type(sig.return_annotation)
    params["__annotations__"][key] = return_type
    params[key] = strawberry.field(resolver=action.fn)


def _wrap_fn_in_data_loader(resolvable: Resolvable):
    data_loader = DataLoader(load_fn=resolvable.batch_fn, max_batch_size=resolvable.max_batch_size)

    sig = inspect.signature(resolvable.fn)

    async def wrapper(self) -> sig.return_annotation:
        key = getattr(self, resolvable.key_arg)
        result = await data_loader.load(key)
        return result

    return wrapper
