from abc import abstractmethod, ABC
from typing import Type, Optional

SchemaFactory = "servey.servey_strawberry.schema_factory.SchemaFactory"


class EntityFactoryABC(ABC):
    priority: int = 100

    @abstractmethod
    def create_type(
        self, annotation: Type, schema_factory: SchemaFactory
    ) -> Optional[Type]:
        """Create a type"""

    @abstractmethod
    def create_input(
        self, annotation: Type, schema_factory: SchemaFactory
    ) -> Optional[Type]:
        """Create an input"""
