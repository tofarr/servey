import inspect
from dataclasses import dataclass
from datetime import datetime

from marshy.types import ExternalItemType

from servey.finder.action_finder_abc import find_actions_with_trigger_type, find_actions
from servey.trigger.web_trigger import WebTrigger, WebTriggerMethod
from servey.servey_aws.serverless.yml_config.yml_config_abc import (
    YmlConfigABC,
    ensure_ref_in_file,
    GENERATED_HEADER,
    create_yml_file,
)
from servey.util import get_servey_main


@dataclass
class AppsyncConfig(YmlConfigABC):
    """
    Set up some aspect of the serverless environment yml files. (For example, functions, resources, etc...)
    """

    servey_actions_yml_file: str = "serverless_servey/appsync.yml"
    servey_appsync_schema_file: str = "serverless_servey/schema.graphql"

    def configure(self, main_serverless_yml_file: str):
        ensure_ref_in_file(
            main_serverless_yml_file,
            ["custom", "appSync"],
            self.servey_actions_yml_file,
        )
        self.build_appsync_schema()
        servey_action_functions_yml = self.build_servey_action_functions_yml()
        create_yml_file(self.servey_actions_yml_file, servey_action_functions_yml)

    def build_appsync_schema(self):
        from servey.servey_strawberry.schema_factory import create_schema

        with open(self.servey_appsync_schema_file, "w") as writer:
            writer.write("# ")
            writer.write(GENERATED_HEADER.replace("\n", "\n# "))
            writer.write(f"\n# Updated at: {datetime.now().isoformat()}\n\n")
            schema = create_schema()

            schema = str(schema)

            # Using string manipulation here feels really gross, but I have not been able to
            # get directives working in strawberry...

            # noinspection SpellCheckingInspection
            schema = schema.replace(
                '\n"""Date with time (isoformat)"""\nscalar DateTime\n', ""
            )
            # Ugly AWS variable substitution
            schema = schema.replace(": DateTime", ": AWSDateTime")
            schema = schema.replace(": UUID", ": ID")
            writer.write(schema)

    def build_servey_action_functions_yml(self) -> ExternalItemType:
        appsync_definitions = {
            "name": get_servey_main(),
            "authenticationType": "API_KEY",
            "defaultMappingTemplates": {"request": False, "response": False},
            "mappingTemplates": [],
            "dataSources": [],
            "schema": self.servey_appsync_schema_file,
            # caching:
            #    behavior: FULL_REQUEST_CACHING  # or PER_RESOLVER_CACHING. Required
            #    ttl: 3600  # The TTL of the cache. Optional. Default: 3600
            #    atRestEncryption:  # Bool, Optional. Enable at rest encryption. disabled by default.
            #    transitEncryption:  # Bool, Optional. Enable transit encryption. disabled by default.
            #    type: 'T2_SMALL'  # Cache instance size. Optional. Default: 'T2_SMALL'
        }
        for action, trigger in find_actions_with_trigger_type(WebTrigger):
            field = action.name.title().replace("_", "")
            mapping_template = {
                "dataSource": action.name,
                "type": "Query"
                if trigger.method == WebTriggerMethod.GET
                else "Mutation",
                "field": field[0].lower() + field[1:],
                # caching:
                #    keys:  # array. A list of VTL variables to use as cache key.
                #        - '$context.identity.sub'
                #        - '$context.arguments.id'
                #    ttl: 1000  # override the ttl for this resolver. (default comes from global config)
            }
            appsync_definitions["mappingTemplates"].append(mapping_template)
            data_source = {
                "name": action.name,
                "type": "AWS_LAMBDA",
                "config": {
                    "functionName": action.name,
                },
            }
            if action.description:
                data_source["description"] = action.description.strip()
            appsync_definitions["dataSources"].append(data_source)

        for action in find_actions():
            sig = inspect.signature(action.fn)
            params = list(sig.parameters.values())
            if params and params[0].name == "self":
                type_name, field_name = action.fn.__qualname__.split(".")
                field_name = field_name[0] + field_name.title()[1:].replace("_", "")
                mapping_template = {
                    "dataSource": action.name,
                    "type": type_name,
                    "field": field_name
                    # caching:
                    #    keys:  # array. A list of VTL variables to use as cache key.
                    #        - '$context.identity.sub'
                    #        - '$context.arguments.id'
                    #    ttl: 1000  # override the ttl for this resolver. (default comes from global config)
                }
                appsync_definitions["mappingTemplates"].append(mapping_template)
                # noinspection PyTypeChecker
                data_source = next(
                    (
                        d
                        for d in appsync_definitions["dataSources"]
                        if d["name"] == action.name
                    ),
                    None,
                )
                if not data_source:
                    data_source = {
                        "name": action.name,
                        "type": "AWS_LAMBDA",
                        "config": {
                            "functionName": action.name,
                        },
                    }
                    if action.description:
                        data_source["description"] = action.description.strip()
                    appsync_definitions["dataSources"].append(data_source)

        return appsync_definitions
