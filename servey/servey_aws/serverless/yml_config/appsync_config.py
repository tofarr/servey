import os

from marshy.types import ExternalItemType
from ruamel.yaml import YAML

from servey.action.finder.action_finder_abc import find_actions_with_trigger_type
from servey.action.trigger.web_trigger import WebTrigger, WebTriggerMethod
from servey.servey_aws.serverless.yml_config.yml_config_abc import YmlConfigABC, ensure_ref_in_file


class AppsyncConfig(YmlConfigABC):
    """
    Set up some aspect of the serverless environment yml files. (For example, functions, resources, etc...)
    """
    servey_actions_yml_file: str = 'serverless_servey_appsync.yml'
    servey_appsync_schema_file: str = 'servey_appsync.schema'

    def configure(self, main_serverless_yml_file: str):
        ensure_ref_in_file(main_serverless_yml_file, ['custom', 'appsync'], self.servey_actions_yml_file)
        self.build_appsync_schema()
        servey_action_functions_yml = self.build_servey_action_functions_yml()
        with open(self.servey_actions_yml_file, 'w') as writer:
            yaml = YAML()
            yaml.dump(servey_action_functions_yml, writer)

    def build_appsync_schema(self):
        from servey.servey_strawberry.schema_factory import new_schema_for_actions
        with open(self.servey_appsync_schema_file, 'w') as writer:
            writer.write(str(new_schema_for_actions()))

    def build_servey_action_functions_yml(self) -> ExternalItemType:
        appsync_definitions = {
            "name": os.environ.get("SERVICE_NAME") or 'servey_app',
            "authenticationType": "AWS_IAM",
            "mappingTemplates": [],
            "dataSources": {},
            "schema": self.servey_appsync_schema_file
        }
        for action, trigger in find_actions_with_trigger_type(WebTrigger):
            field = action.action_meta.name.title().replace('_', '')
            appsync_definitions['mappingTemplates'].append({
                "type": "Query" if trigger.method == WebTriggerMethod.GET else "Mutation",
                "field": field[0] + field[1:],
                "request": "requestMappingTemplate.vtl",
                "response": "responseMappingTemplate.vtl"
            })

        return appsync_definitions
