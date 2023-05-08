import dataclasses
import inspect
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Type, Set

from marshy.factory.optional_marshaller_factory import get_optional_type
from marshy.types import ExternalItemType
from ruamel.yaml import YAML

from servey.action.action import Action, get_action
from servey.finder.action_finder_abc import find_actions_with_trigger_type
from servey.trigger.web_trigger import WebTrigger, WebTriggerMethod
from servey.servey_aws.serverless.yml_config.yml_config_abc import (
    YmlConfigABC,
    GENERATED_HEADER,
    create_yml_file,
)
from servey.util import get_servey_main, attr_camel_case


@dataclass
class AppsyncConfig(YmlConfigABC):
    """
    Set up some aspect of the serverless environment yml files. (For example, functions, resources, etc...)
    """

    servey_actions_yml_file: str = "serverless_servey/appsync.yml"
    servey_appsync_schema_file: str = "serverless_servey/schema.graphql"
    use_router_for_all: bool = field(
        default_factory=lambda: int(os.environ.get("SERVEY_AWS_ROUTER_FOR_ALL", "0"))
        == 1
    )

    def configure(self, main_serverless_yml_file: str):
        yaml = YAML()
        with open(main_serverless_yml_file, "r") as reader:
            root = yaml.load(reader)
            root["appSync"] = "${file(" + self.servey_actions_yml_file + ")}"
        with open(main_serverless_yml_file, "w") as writer:
            yaml.dump(root, writer)
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
                '"""Date with time (isoformat)"""\nscalar DateTime\n', ""
            )
            schema = schema.replace("scalar UUID\n", "")
            # Ugly AWS variable substitution
            schema = schema.replace(": DateTime", ": AWSDateTime")
            schema = schema.replace(": UUID", ": ID")
            writer.write(schema)

    def build_servey_action_functions_yml(self) -> ExternalItemType:
        appsync_definitions = {
            "name": get_servey_main(),
            "authentication": {
                "type": "API_KEY",
            },
            "apiKeys": [
                {
                    "name": f"{get_servey_main()}Key",
                }
            ],
            "resolvers": {},
            "dataSources": {},
            "schema": self.servey_appsync_schema_file,
        }
        processed_dataclasses = set()
        for action, trigger in find_actions_with_trigger_type(WebTrigger):
            resolver_type = (
                "Query" if trigger.method == WebTriggerMethod.GET else "Mutation"
            )
            resolver_name = resolver_type + "." + attr_camel_case(action.name)
            self.add_field(action, appsync_definitions, resolver_name)
            self.build_nested_resolvers(
                action, appsync_definitions, processed_dataclasses
            )

        return appsync_definitions

    def add_field(
        self, action: Action, appsync_definitions: ExternalItemType, resolver_name: str
    ):
        # data source may be
        use_router = self.use_router_for_all or "<locals>" in action.fn.__qualname__
        data_source_name = "servey_router" if use_router else action.name
        resolver = {
            "kind": "UNIT",
            "dataSource": data_source_name,
        }
        if action.batch_invoker:
            resolver["maxBatchSize"] = action.batch_invoker.max_batch_size
        appsync_definitions["resolvers"][resolver_name] = resolver
        data_source = {
            "type": "AWS_LAMBDA",
            "config": {
                "functionName": data_source_name,
            },
        }
        if action.description and not use_router:
            data_source["description"] = action.description.strip()
        appsync_definitions["dataSources"][data_source_name] = data_source

    def build_nested_resolvers(
        self,
        action: Action,
        appsync_definitions: ExternalItemType,
        processed_dataclasses: Set[Type],
    ):
        sig = inspect.signature(action.fn)
        type_ = sig.return_annotation
        type_ = get_optional_type(type_) or type_
        if not dataclasses.is_dataclass(type_) or type_ in processed_dataclasses:
            return
        processed_dataclasses.add(type_)
        members = inspect.getmembers(type_)
        for name, member in members:
            nested_action = get_action(member)
            if nested_action:
                resolver_name = type_.__name__ + "." + attr_camel_case(name)
                self.add_field(nested_action, appsync_definitions, resolver_name)
                self.build_nested_resolvers(
                    nested_action, appsync_definitions, processed_dataclasses
                )
