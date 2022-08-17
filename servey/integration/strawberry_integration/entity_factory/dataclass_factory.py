from typing import Type, Optional

import strawberry

from servey.integration.strawberry_integration.entity_factory.entity_factory_abc import (
    EntityFactoryABC,
)
from servey.integration.strawberry_integration.schema_factory import SchemaFactory


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
        type_ = strawberry.type(annotation, description=annotation.__doc__)
        schema_factory.types[annotation.__name__] = type_
        # noinspection PyDataclass
        for field in fields(type_):
            field.type = schema_factory.create_type(field.type)
        return type_

    def create_input(
        self, annotation: Type, schema_factory: SchemaFactory
    ) -> Optional[Type]:
        if not is_dataclass(annotation):
            return
        name = f"{annotation.__name__}Input"
        input = schema_factory.inputs.get(name)
        if input:
            return input
        input = strawberry.input(annotation, name=name, description=annotation.__doc__)
        schema_factory.inputs[name] = input
        # noinspection PyDataclass
        for field in fields(input):
            field.type = schema_factory.create_input(field.type)
        return input
