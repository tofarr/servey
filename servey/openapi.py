from marshy.types import ExternalItemType
from schemey.json_output_context import JsonOutputContext
from schemey.object_schema import OBJECT

from servey.action import Action
from servey.servey_context import ServeyContext
from servey.util import filter_none


def openapi_schema(servey_context: ServeyContext, api_prefix: str = "/api") -> ExternalItemType:
    json_output_context = JsonOutputContext(defs_path='components/schemas')
    paths = {}
    for a in servey_context.actions_by_name.values():
        action_to_path(a, paths, json_output_context, api_prefix)
    schema = {
        "openapi": "3.0.2",
        "info": filter_none({
            "title": servey_context.name,
            "description": servey_context.description,
            "version": servey_context.version
        }),
        "paths": paths,
        "components": {
            "schemas": json_output_context.defs
        }
    }
    return schema


def action_to_path(action: Action, paths: ExternalItemType, json_output_context: JsonOutputContext, api_prefix: str):
    path = paths.get(api_prefix + action.path)
    if path is None:
        path = paths[api_prefix + action.path] = {}
    for method in action.http_methods:
        request_json_properties = {
            p.name: p.to_json_schema(json_output_context)
            for p in action.params_schema.property_schemas
        }
        path[method.value.lower()] = {
            'summary': action.doc,
            'operationId': f"{method.value.lower()}_{action.name}",
            'requestBody': {
                'content': {
                    'application/json': {
                        'schema': dict(type=OBJECT, properties=request_json_properties, additionalProperties=False)
                    }
                },
                'required': bool(request_json_properties)
            },
            'responses': {
                200: {
                    'description': "Success",
                    'content': {
                        'application/json': {
                            'schema': action.return_schema.to_json_schema(json_output_context)
                        }
                    }
                }
            }
        }
    return path



