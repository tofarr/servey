from dataclasses import dataclass, field
from typing import Type

from strawberry import LazyType

from servey.servey_strawberry.schema_factory import SchemaFactory


@dataclass(frozen=True)
class SchemaFactoryLazyType(LazyType):
    """
    This is a bit of a hack - pretend to be a standard LazyType to get strawberry to resolve the type
    """

    schema_factory: SchemaFactory = field(repr=False, hash=False, default=None)

    def resolve_type(self) -> Type:
        return self.schema_factory.types.get(self.type_name)

    def __call__(self):  # pragma: no cover
        # this empty call method allows SchemaFactoryLazyInput to be used in generic types
        return None

    @property
    def __name__(self):
        return self.type_name
