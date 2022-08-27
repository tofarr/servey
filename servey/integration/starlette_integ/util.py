from marshy.types import ExternalItemType, ExternalType


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
