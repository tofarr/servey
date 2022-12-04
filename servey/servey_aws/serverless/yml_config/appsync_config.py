import os
from datetime import datetime

from marshy.types import ExternalItemType
from ruamel.yaml import YAML

from servey.action.finder.action_finder_abc import find_actions_with_trigger_type
from servey.action.trigger.web_trigger import WebTrigger, WebTriggerMethod
from servey.servey_aws.serverless.yml_config.yml_config_abc import (
    YmlConfigABC,
    ensure_ref_in_file,
    GENERATED_HEADER,
)


class AppsyncConfig(YmlConfigABC):
    """
    Set up some aspect of the serverless environment yml files. (For example, functions, resources, etc...)
    """

    servey_actions_yml_file: str = "serverless_servey_appsync.yml"
    servey_appsync_schema_file: str = "servey_appsync.graphql"

    def configure(self, main_serverless_yml_file: str):
        ensure_ref_in_file(
            main_serverless_yml_file,
            ["custom", "appSync"],
            self.servey_actions_yml_file,
        )
        self.build_appsync_schema()
        servey_action_functions_yml = self.build_servey_action_functions_yml()
        with open(self.servey_actions_yml_file, "w") as writer:
            writer.write("# ")
            writer.write(GENERATED_HEADER.replace("\n", "\n# "))
            writer.write(f"\n# Updated at: {datetime.now().isoformat()}\n\n")
            yaml = YAML()
            yaml.dump(servey_action_functions_yml, writer)

    def build_appsync_schema(self):
        from servey.servey_strawberry.schema_factory import new_schema_for_actions

        with open(self.servey_appsync_schema_file, "w") as writer:
            writer.write("# ")
            writer.write(GENERATED_HEADER.replace("\n", "\n# "))
            writer.write(f"\n# Updated at: {datetime.now().isoformat()}\n\n")
            schema = str(new_schema_for_actions())
            schema = schema.replace(
                '\n"""Date with time (isoformat)"""\nscalar DateTime\n', ""
            )
            schema = schema.replace("DateTime", "AWSDateTime")
            writer.write(schema)

    def build_servey_action_functions_yml(self) -> ExternalItemType:
        appsync_definitions = {
            "name": os.environ.get("SERVICE_NAME") or "servey_app",
            "authenticationType": "API_KEY",
            "defaultMappingTemplates": {"request": False, "response": False},
            "mappingTemplates": [],
            "dataSources": [],
            "schema": self.servey_appsync_schema_file,
        }
        for action, trigger in find_actions_with_trigger_type(WebTrigger):
            action_meta = action.action_meta
            field = action_meta.name.title().replace("_", "")
            mapping_template = {
                "dataSource": action_meta.name,
                "type": "Query"
                if trigger.method == WebTriggerMethod.GET
                else "Mutation",
                "field": field[0].lower() + field[1:],
                # TODO: Configure caching here!
            }
            appsync_definitions["mappingTemplates"].append(mapping_template)
            data_source = {
                "name": action_meta.name,
                "type": "AWS_LAMBDA",
                "config": {
                    "functionName": action_meta.name,
                },
            }
            if action_meta.description:
                data_source["description"] = action_meta.description.strip()
            appsync_definitions["dataSources"].append(data_source)

        return appsync_definitions
