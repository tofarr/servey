import inspect
from datetime import datetime
from typing import Type, Optional
from uuid import UUID

from servey.integration.strawberry_integration.entity_factory.entity_factory_abc import (
    EntityFactoryABC,
)
from servey.integration.strawberry_integration.schema_factory import SchemaFactory


class GenericFactory(EntityFactoryABC):
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
