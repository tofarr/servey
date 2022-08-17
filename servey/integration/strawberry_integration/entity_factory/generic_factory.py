import inspect
from enum import Enum
from typing import Type, Optional

import strawberry
import typing_inspect
from marshy.utils import resolve_forward_refs

from servey.integration.strawberry_integration.entity_factory.entity_factory_abc import (
    EntityFactoryABC,
)
from servey.integration.strawberry_integration.schema_factory import SchemaFactory


class GenericFactory(EntityFactoryABC):
    priority: int = 150

    def create_type(
        self, annotation: Type, schema_factory: SchemaFactory
    ) -> Optional[Type]:
        origin = typing_inspect.get_origin(annotation)
        if origin:
            origin = schema_factory.create_type(origin)
            args = tuple(
                schema_factory.create_type(a)
                for a in typing_inspect.get_args(annotation)
            )
            return origin[args]

    def create_input(
        self, annotation: Type, schema_factory: SchemaFactory
    ) -> Optional[Type]:
        origin = typing_inspect.get_origin(annotation)
        if origin:
            origin = schema_factory.create_type(origin)
            args = tuple(
                schema_factory.create_type(a)
                for a in typing_inspect.get_args(annotation)
            )
            return origin[args]
