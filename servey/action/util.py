import inspect
from copy import deepcopy
from typing import Callable

from marshy.types import ExternalItemType, ExternalType
from schemey import Schema


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


# noinspection PyTypeChecker
def strip_injected_from_schema(schema: Schema, inject_at: str) -> Schema:
    result = deepcopy(schema.schema)
    current = result
    path = inject_at.split(".")
    for p in path[:-1]:
        current = current["properties"][p]
    del current["properties"][path[-1]]
    if current["required"]:
        current["required"] = [r for r in current["required"] if r != path[-1]]
    result_schema = Schema(current, schema.python_type)
    return result_schema


# noinspection PyTypeChecker
def wrap_fn_for_injection(
    fn: Callable, inject_at: str, value_factory: Callable
) -> Callable:
    sig = inspect.signature(fn)
    path = inject_at.split(".")
    if len(path) == 1:
        sig = sig.replace(
            parameters=tuple(p for p in sig.parameters.values() if p.name != inject_at)
        )

    def wrapper(**kwargs):
        value = value_factory()
        inject_value_at(inject_at, kwargs, value)
        result = fn(**kwargs)
        return result

    wrapper.__signature__ = sig
    return wrapper
