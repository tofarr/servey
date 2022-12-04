from dataclasses import is_dataclass, fields, dataclass
from typing import Type, Optional

import strawberry

from servey.servey_strawberry.entity_factory.entity_factory_abc import (
    EntityFactoryABC,
)
from servey.servey_strawberry.schema_factory import SchemaFactory


class DataclassFactory(EntityFactoryABC):
    priority: int = 120

    def create_type(
        self, annotation: Type, schema_factory: SchemaFactory
    ) -> Optional[Type]:
        if not is_dataclass(annotation):
            return
        type_ = schema_factory.types.get(annotation.__name__)
        if type_:
            return type_

        params = {"__annotations__": {}}
        for f in fields(annotation):
            params["__annotations__"][f.name] = schema_factory.get_type(f.type)

        """
        # noinspection PyDataclass
        params = {
            '__annotations__': {
                f.name: schema_factory.get_type(f.type) for f in fields(annotation)
            },
        }
        """
        wrap_type = dataclass(type(annotation.__name__, tuple(), params))
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
