import os
from dataclasses import dataclass, field

from marshy.factory.impl_marshaller_factory import get_impls
from marshy.types import ExternalItemType
from schemey.util import filter_none

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


@dataclass
class ActionFunctionConfig(YmlConfigABC):
    """
    Set up some aspect of the serverless environment yml files. (For example, functions, resources, etc...)
    """

    actions_yml_file: str = "serverless_servey/actions.yml"
    use_router_for_all: bool = field(
        default_factory=lambda: int(os.environ.get("SERVEY_AWS_ROUTER_FOR_ALL", "0"))
        == 1
    )
    router_name: str = "servey_router"

    def configure(self, main_serverless_yml_file: str):
        ensure_ref_in_file(
            main_serverless_yml_file, ["functions"], self.actions_yml_file
        )
        action_functions_yml = self.build_action_functions_yml()
        create_yml_file(self.actions_yml_file, action_functions_yml)

    def build_action_functions_yml(self) -> ExternalItemType:
        lambda_definitions = {}
        trigger_handlers = [h() for h in get_impls(TriggerHandlerABC)]
        connection_table_name = get_servey_main() + "_connection"
        for action in find_actions():
            use_router = self.use_router_for_all or "<locals>" in action.fn.__qualname__
            if use_router:
                lambda_name = self.router_name
                lambda_definition = lambda_definitions.get(lambda_name)
                if not lambda_definition:
                    lambda_definition = lambda_definitions[lambda_name] = dict(
                        handler="servey.servey_aws.lambda_router.invoke",
                        timeout=30,
                    )
            else:
                # noinspection PyUnresolvedReferences
                lambda_definition = lambda_definitions[action.name] = filter_none(
                    dict(
                        handler="servey.servey_aws.lambda_invoker.invoke",
                        description=action.description.strip()
                        if action.description
                        else None,
                        timeout=action.timeout,
                        environment=dict(
                            SERVEY_ACTION_MODULE=action.fn.__module__,
                            SERVEY_ACTION_FUNCTION_NAME=action.fn.__qualname__,
                            CONNECTION_TABLE_NAME=connection_table_name,
                        ),
                    )
                )
            for trigger in action.triggers:
                for handler in trigger_handlers:
                    handler.handle_trigger(action, trigger, lambda_definition)
        for subscription in find_subscriptions():
            for action in subscription.action_subscribers:
                if action.name in lambda_definitions:
                    lambda_definition = lambda_definitions[action.name]
                else:
                    lambda_definition = lambda_definitions[self.router_name]
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
