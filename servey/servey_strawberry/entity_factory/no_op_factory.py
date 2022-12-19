from datetime import datetime
from typing import Type, Optional
from uuid import UUID

from servey.servey_strawberry.entity_factory.entity_factory_abc import (
    EntityFactoryABC,
)
from servey.servey_strawberry.schema_factory import SchemaFactory


class NoOpFactory(EntityFactoryABC):
    priority: int = 150

    def create_type(
        self, annotation: Type, schema_factory: SchemaFactory
    ) -> Optional[Type]:
        if annotation in (bool, datetime, float, int, str, UUID):
            return annotation

    def create_input(
        self, annotation: Type, schema_factory: SchemaFactory
    ) -> Optional[Type]:
        return self.create_type(annotation, schema_factory)
