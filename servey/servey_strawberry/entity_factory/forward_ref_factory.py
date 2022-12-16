from typing import Type, Optional

import typing_inspect
from marshy.utils import resolve_forward_refs

from servey.servey_strawberry.entity_factory.entity_factory_abc import (
    EntityFactoryABC,
)
from servey.servey_strawberry.schema_factory import SchemaFactory


class ForwardRefFactory(EntityFactoryABC):
    priority: int = 200

    def create_type(
        self, annotation: Type, schema_factory: SchemaFactory
    ) -> Optional[Type]:
        if typing_inspect.is_forward_ref(annotation):
            annotation = resolve_forward_refs(annotation)
            return schema_factory.get_type(annotation)

    def create_input(
        self, annotation: Type, schema_factory: SchemaFactory
    ) -> Optional[Type]:
        if typing_inspect.is_forward_ref(annotation):
            annotation = resolve_forward_refs(annotation)
            return schema_factory.get_input(annotation)
