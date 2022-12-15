import inspect
from copy import deepcopy
from typing import Callable, Optional, Tuple, Set

from marshy import get_default_context
from marshy.marshaller.marshaller_abc import MarshallerABC
from marshy.marshaller.obj_marshaller import ObjMarshaller, attr_config
from marshy.marshaller_context import MarshallerContext
from marshy.types import ExternalItemType, ExternalType
from schemey import Schema, get_default_schema_context, SchemaContext

from servey.errors import ServeyError


def get_schema_for_params(
    fn: Callable, skip_args: Set[str], schema_context: Optional[SchemaContext] = None
) -> Schema:
    if not schema_context:
        schema_context = get_default_schema_context()
    sig = inspect.signature(fn)
    properties = {}
    required = []
    params = list(sig.parameters.values())
    for i, p in enumerate(params):
        if p.name in skip_args:
            continue
        if p.annotation is inspect.Parameter.empty:
            raise ServeyError(f"missing_param_annotation:{fn.__name__}:{p.name}")
        properties[p.name] = schema_context.schema_from_type(p.annotation).schema
        if p.default == inspect.Parameter.empty:
            required.append(p.name)
    json_schema = {
        "type": "object",
        "properties": properties,
        "additionalProperties": False,
        "required": required,
    }
    schema = Schema(json_schema, dict)
    return schema


def get_schema_for_result(fn: Callable) -> Schema:
    schema_context = get_default_schema_context()
    sig = inspect.signature(fn)
    type_ = sig.return_annotation
    if type_ is inspect.Parameter.empty:
        raise ServeyError(f"missing_return_annotation:{fn.__name__}")
    schema = schema_context.schema_from_type(type_)
    return schema


def get_marshaller_for_params(
    fn: Callable,
    skip_args: Set[str],
    marshaller_context: Optional[MarshallerContext] = None,
) -> MarshallerABC:
    if not marshaller_context:
        marshaller_context = get_default_context()
    sig = inspect.signature(fn)
    attr_configs = []
    params = list(sig.parameters.values())
    for p in params:
        if p.name in skip_args:
            continue
        if p.annotation is inspect.Parameter.empty:
            raise TypeError(f"missing_param_annotation:{fn.__name__}({p.name}")
        attr_configs.append(
            attr_config(marshaller_context.get_marshaller(p.annotation), p.name)
        )
    marshaller = ObjMarshaller(dict, tuple(attr_configs))
    return marshaller


def with_isolated_references(
    root: ExternalItemType, schema: ExternalType, components: ExternalItemType
):
    if isinstance(schema, dict):
        ref = schema.get("$ref")
        if ref is not None:
            ref = ref.split("/")
            referenced_schema = root
            for r in ref:
                referenced_schema = referenced_schema[r]
            name = referenced_schema.get("name")
            if name not in components:
                components[name] = schema  # Prevent infinite loop
                components[name] = with_isolated_references(
                    root, referenced_schema, components
                )
            return {"$ref": f"components/{name}"}
        schema = {
            k: with_isolated_references(root, v, components) for k, v in schema.items()
        }
        return schema
    elif isinstance(schema, list):
        schema = [with_isolated_references(root, v, components) for v in schema]
        return schema
    else:
        return schema


def inject_value_at(path: str, current, value):
    path = path.split(".")
    parent_path = path[:-1]
    for p in parent_path:
        if hasattr(current, p):
            current = getattr(current, p)
        else:
            current = current[p]
    p = path[-1]
    if hasattr(current, p):
        setattr(current, p, value)
    else:
        current[p] = value
