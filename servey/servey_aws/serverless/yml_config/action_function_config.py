from marshy.factory.impl_marshaller_factory import get_impls
from marshy.types import ExternalItemType
from ruamel.yaml import YAML

from servey.action.finder.action_finder_abc import find_actions
from servey.servey_aws.serverless.trigger_handler.trigger_handler_abc import TriggerHandlerABC
from servey.servey_aws.serverless.yml_config.yml_config_abc import YmlConfigABC, ensure_ref_in_file


class ActionFunctionConfig(YmlConfigABC):
    """
    Set up some aspect of the serverless environment yml files. (For example, functions, resources, etc...)
    """
    servey_actions_yml_file: str = 'serverless_servey_actions.yml'

    def configure(self, main_serverless_yml_file: str):
        ensure_ref_in_file(main_serverless_yml_file, ['functions'], self.servey_actions_yml_file)
        servey_action_functions_yml = self.build_servey_action_functions_yml()
        with open(self.servey_actions_yml_file, 'w') as writer:
            yaml = YAML()
            yaml.dump(servey_action_functions_yml, writer)

    @staticmethod
    def build_servey_action_functions_yml() -> ExternalItemType:
        lambda_definitions = {}
        trigger_handlers = [h() for h in get_impls(TriggerHandlerABC)]
        for action in find_actions():
            action_meta = action.action_meta
            lambda_definition = lambda_definitions[action_meta.name] = dict(
                handler=f'servey.servey_aws.lambda_app.{action_meta.name}',
                timeout=action_meta.timeout
            )
            for trigger in action_meta.triggers:
                for handler in trigger_handlers:
                    handler.handle_trigger(action_meta, trigger, lambda_definition)
        return lambda_definitions