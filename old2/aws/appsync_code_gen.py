"""
Code generator for AWS / serverless / Appsync. Generates a graphql schema and updates definitions in the serverless yaml
"""
from typing import Callable, Any, Optional

from marshy.types import ExternalItemType
from ruamel.yaml import YAML

from servey import ActionType
from servey import graphql_schema
from servey import ServeyContext


def refresh_schema_file(context: ServeyContext, schema_file: str = 'graphql.schema'):
    with open(schema_file, 'w') as f:
        schema = graphql_schema(context)
        schema.to_graphql(f)

def update_serverless_yaml(context: ServeyContext, in_file: str = 'serverless.yml', out_file: Optional[str] = None):
    yaml = YAML(typ='safe')  # default, if not specfied, is 'rt' (round-trip)
    with open(in_file, 'r') as f:
        serverless_yaml = yaml.load(f)
    inject_functions(context, serverless_yaml)
    inject_mapping_templates(context, serverless_yaml)
    TODO: I need to research appsync mapping templates here as I dont know enough about them. Do this tonight
    Appsync mapping templates are just as horrible as I remember. They map request headers / body / url to function params
    and vice versa

    FINALLY, I ALSO NEED TO INTEGRATE SUBSCRIPTIONS HERE (AND I AM NOT FULLY SURE HOW THOSE ARE INVOKES SERVER SIDE EITHER)

    THE NAMES / URL MAPPINGS ON META MAY NOT BE RIGHT EITHER - STANDARDISATION IS KEY.

    CLIENT SIDE CODE SHOULD BE CAPABLE OF GENERATING STUBS BASED ON THE JSON ENDPOINT. (EITHER ON THE FLY OR AT REST)


    I DONT LIKE THE ACTION NAME WORK. DIFFERENT CASES OF THIS ARE CONFUSING
    I DONT LIKE THE SEPARATE AUTHORIZER. THIS KIND OF GUMS UP THE SYSTEM. IT FEELS LIKE INPUT MAPPINGS ARE IN ORDER
    I DONT LIKE THE ACTION MAPPING. IT DOES NOT WORK WELL FOR HTTP (ONE ONLY), AND THE TRANSLATION IS NOT COMFORTABLE OR DIRECT
        THIS NEEDS RETHINKING.
        MAYBE WE MAKE IT MORE GENERIC

    inject_data_sources(context, serverless_yaml)
    with open(out_file or in_file, 'w') as f:
        yaml.dump(serverless_yaml, f)


def inject_functions(context: ServeyContext, yaml: ExternalItemType):
    """
    Inject function definitions into the yaml given for use by appsync. Pre-existing functions may have
    their handler / description updated. Does not inject any handlers (e.g.: For api gateway or periodic
    invocation)
    """
    functions: ExternalItemType = _upsert('functions', yaml)
    for action in context.actions_by_name.values():
        function: ExternalItemType = _upsert(action.name, functions)
        function['handler'] = action.callable.__module__ + '.' + action.callable.__name__
        if action.doc:
            function['description'] = action.doc


def inject_mapping_templates(context: ServeyContext, yaml: ExternalItemType):
    custom = _upsert('custom', yaml)
    appsync_yaml = _upsert('appSync', custom)
    mapping_templates_yaml = _upsert('mappingTemplates', appsync_yaml, list)
    for action in context.actions_by_name.values():
        mapping_template = next((m for m in mapping_templates_yaml if m.get('field') == action.name), None)
        if mapping_template is None:
            mapping_template = dict(field=action.name)
            mapping_templates_yaml.append(mapping_template)
        mapping_template['dataSource'] = f'{action.name}DataSource'
        mapping_template['type'] = 'Query' if action.action_type in [ActionType.GET, ActionType.HEAD] else 'Mutation'


def inject_data_sources(context: ServeyContext, yaml: ExternalItemType):
    custom = _upsert('custom', yaml)
    appsync_yaml = _upsert('appSync', custom)
    data_sources_yaml = _upsert('dataSources', appsync_yaml, list)
    for action in context.actions_by_name.values():
        name = f'{action.name}DataSource'
        data_source = next((m for m in data_sources_yaml if m.get('name') == name), None)
        if data_source is None:
            data_source = dict(name=name)
            data_sources_yaml.append(data_source)
        data_source['type'] = 'AWS_LAMBDA'
        data_source['config'] = dict(lambdaFunctionArn={'Fn::GetAtt': [action.name, 'Arn']})


def _upsert(name: str, target_yaml: ExternalItemType, factory: Callable[[], Any] = dict):
    node = target_yaml.get(name)
    if node is None:
        node = factory()
        target_yaml[name] = node
    return node
