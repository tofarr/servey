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


class ForwardRefFactory(EntityFactoryABC):
    priority: int = 200

    def create_type(
        self, annotation: Type, schema_factory: SchemaFactory
    ) -> Optional[Type]:
        if typing_inspect.is_forward_ref(annotation):
            annotation = resolve_forward_refs(annotation)
            return schema_factory.create_type(annotation)

    def create_input(
        self, annotation: Type, schema_factory: SchemaFactory
    ) -> Optional[Type]:
        if typing_inspect.is_forward_ref(annotation):
            annotation = resolve_forward_refs(annotation)
            return schema_factory.create_input(annotation)