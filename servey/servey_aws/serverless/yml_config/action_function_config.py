from marshy.factory.impl_marshaller_factory import get_impls
from marshy.types import ExternalItemType

from servey.finder.action_finder_abc import find_actions
from servey.finder.subscription_finder_abc import find_subscriptions
from servey.servey_aws.serverless.trigger_handler.trigger_handler_abc import (
    TriggerHandlerABC,
)
from servey.servey_aws.serverless.yml_config.yml_config_abc import (
    YmlConfigABC,
    ensure_ref_in_file,
    create_yml_file,
)
from servey.util import get_servey_main


class ActionFunctionConfig(YmlConfigABC):
    """
    Set up some aspect of the serverless environment yml files. (For example, functions, resources, etc...)
    """

    actions_yml_file: str = "serverless_servey/actions.yml"

    def configure(self, main_serverless_yml_file: str):
        ensure_ref_in_file(
            main_serverless_yml_file, ["functions"], self.actions_yml_file
        )
        action_functions_yml = self.build_action_functions_yml()
        create_yml_file(self.actions_yml_file, action_functions_yml)

    @staticmethod
    def build_action_functions_yml() -> ExternalItemType:
        lambda_definitions = {}
        trigger_handlers = [h() for h in get_impls(TriggerHandlerABC)]
        connection_table_name = get_servey_main() + "_connection"
        for action in find_actions():
            # noinspection PyUnresolvedReferences
            lambda_definition = lambda_definitions[action.name] = dict(
                handler=f"servey.servey_aws.lambda_invoker.invoke",
                timeout=action.timeout,
                environment=dict(
                    SERVEY_ACTION_MODULE=action.fn.__module__,
                    SERVEY_ACTION_FUNCTION_NAME=action.fn.__qualname__,
                    CONNECTION_TABLE_NAME=connection_table_name,
                ),
            )
            if action.description:
                lambda_definition["description"] = action.description.strip()
            for trigger in action.triggers:
                for handler in trigger_handlers:
                    handler.handle_trigger(action, trigger, lambda_definition)
        for subscription in find_subscriptions():
            for action in subscription.action_subscribers:
                lambda_definition = lambda_definitions[action.name]
                events = lambda_definition.get("events")
                if not events:
                    events = lambda_definition["events"] = []
                events.append(
                    {
                        "sqs": {
                            "arn": {
                                "Fn::GetAtt": [
                                    subscription.name.title().replace("_", "") + "SQS",
                                    "Arn",
                                ]
                            },
                        }
                    }
                )

        return lambda_definitions
