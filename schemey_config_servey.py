from marshy import get_default_context
from schemey.factory.impl_schema_factory import register_marshy_impls
from schemey.schema_context import SchemaContext


priority = 100


def configure(context: SchemaContext):
    register_marshy_impls(context, get_default_context())
