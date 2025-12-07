import inspect
from enum import Enum
from typing import Type, Optional

import strawberry
from marshy.utils import resolve_forward_refs

from servey.servey_strawberry.entity_factory.entity_factory_abc import (
    EntityFactoryABC,
)
from servey.servey_strawberry.schema_factory import SchemaFactory


class EnumFactory(EntityFactoryABC):
    priority: int = 120

    def create_type(
        self, annotation: Type, schema_factory: SchemaFactory
    ) -> Optional[Type]:
        annotation = resolve_forward_refs(annotation)
        if inspect.isclass(annotation) and issubclass(annotation, Enum):
            strawberry_enum = schema_factory.enums.get(annotation.__name__)
            if not strawberry_enum:
                # noinspection PyTypeChecker
                strawberry_enum = schema_factory.enums[
                    annotation.__name__
                ] = strawberry.enum(annotation)
            return strawberry_enum

    def create_input(
        self, annotation: Type, schema_factory: SchemaFactory
    ) -> Optional[Type]:
        return self.create_type(annotation, schema_factory)
