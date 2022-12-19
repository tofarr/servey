from typing import Optional, List, Type

import typing_inspect

from servey.servey_strawberry.entity_factory.entity_factory_abc import (
    EntityFactoryABC,
)
from servey.servey_strawberry.schema_factory import SchemaFactory

_TYPES_BY_ORIGIN = {
    # t.__origin__: t for t in typing.__dict__.values() if hasattr(t, "__origin__")
    list: List,
    set: List,
    frozenset: List,
}


class GenericFactory(EntityFactoryABC):
    priority: int = 150

    def create_type(
        self, annotation: Type, schema_factory: SchemaFactory
    ) -> Optional[Type]:
        origin = typing_inspect.get_origin(annotation)
        if origin:
            origin = _TYPES_BY_ORIGIN.get(origin) or origin
            args = tuple(
                schema_factory.get_type(a) for a in typing_inspect.get_args(annotation)
            )
            # noinspection PyTypeChecker
            return origin[args]

    def create_input(
        self, annotation: Type, schema_factory: SchemaFactory
    ) -> Optional[Type]:
        origin = typing_inspect.get_origin(annotation)
        if origin:
            origin = _TYPES_BY_ORIGIN.get(origin) or origin
            args = tuple(
                schema_factory.get_input(a) for a in typing_inspect.get_args(annotation)
            )
            # noinspection PyTypeChecker
            return origin[args]
