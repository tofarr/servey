import inspect
import os
from typing import Callable, Optional, Set

from marshy import get_default_context
from marshy.marshaller.marshaller_abc import MarshallerABC
from marshy.marshaller.obj_marshaller import ObjMarshaller, attr_config
from marshy.marshaller_context import MarshallerContext
from marshy.types import ExternalItemType, ExternalType
from schemey import Schema, get_default_schema_context, SchemaContext


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
            raise TypeError(f"missing_param_annotation:{fn.__name__}:{p.name}")
        schema = schema_context.schema_from_type(p.annotation).schema
        properties[p.name] = _remap_references(f"#/properties/{p.name}", schema)
        if p.default == inspect.Parameter.empty:
            required.append(p.name)
    json_schema = {
        "type": "object",
        "properties": properties,
        "additionalProperties": os.environ.get("SERVEY_STRICT_SCHEMA") != "1",
        "required": required,
    }
    schema = Schema(json_schema, dict)
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


def _remap_references(to_path: str, schema: ExternalType) -> ExternalType:
    if isinstance(schema, dict):
        ref = schema.get("$ref")
        if ref and ref.startswith("#"):
            return {"$ref": to_path + ref[1:]}
        schema = {k: _remap_references(to_path, v) for k, v in schema.items()}
        return schema
    elif isinstance(schema, list):
        schema = [_remap_references(to_path, i) for i in schema]
        return schema
    else:
        return schema


def move_ref_items_to_components(
    root: ExternalItemType, current: ExternalType, components: ExternalItemType
) -> ExternalType:
    if isinstance(current, dict):
        name = current.get("name")
        if name and isinstance(name, str):
            schema = components.get(name)
            if not schema:
                components[name] = "PENDING"  # Prevent infinite recursion
                components[name] = {
                    k: move_ref_items_to_components(root, v, components)
                    for k, v in current.items()
                }
            return {"$ref": f"#/components/{name}"}
        ref = current.get("$ref")
        if ref and ref.startswith("#/"):
            referenced = root
            if ref != "#/":
                ref = ref[2:].split("/")
                for r in ref:
                    if isinstance(referenced, list):
                        # noinspection PyTypeChecker
                        referenced = referenced[int(r)]
                    else:
                        referenced = referenced[r]
            name = referenced["name"]
            return {"$ref": f"#/components/{name}"}
        schema = {
            k: move_ref_items_to_components(root, v, components)
            for k, v in current.items()
        }
        return schema
    elif isinstance(current, list):
        schema = [move_ref_items_to_components(root, i, components) for i in current]
        return schema
    return current
