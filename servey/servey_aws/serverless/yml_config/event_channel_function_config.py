from dataclasses import field, dataclass
from typing import List

from marshy.types import ExternalItemType

from servey.event_channel.background.background_action_channel import (
    BackgroundActionChannel,
)
from servey.event_channel.event_channel_abc import EventChannelABC
from servey.event_channel.websocket.websocket_event_channel import WebsocketEventChannel
from servey.finder.event_channel_finder_abc import (
    find_event_channels_by_type,
    find_event_channels,
)
from servey.servey_aws.serverless.yml_config.yml_config_abc import (
    YmlConfigABC,
    ensure_ref_in_file,
    create_yml_file,
)
from servey.util import get_servey_main


@dataclass
class EventChannelFunctionConfig(YmlConfigABC):
    """
    Set up some aspect of the serverless environment yml files. (For example, functions, resources, etc...)
    """

    handlers_yml_file: str = "serverless_servey/event_channel_handlers.yml"
    resources_yml_file: str = "serverless_servey/event_channel_resources.yml"
    role_statement_yml_file: str = "serverless_servey/event_channel_role_statement.yml"
    event_channels: List[EventChannelABC] = field(
        default_factory=lambda: list(find_event_channels())
    )

    @property
    def has_websocket_channels(self):
        has_websocket_channels = next(
            (True for _ in find_event_channels_by_type(WebsocketEventChannel)), False
        )
        return has_websocket_channels

    @property
    def connection_table_name(self):
        connection_table_name = get_servey_main() + "_connection"
        return connection_table_name

    def configure(self, main_serverless_yml_file: str):
        if not self.event_channels:
            # Should we remove files if missing?
            return

        if self.has_websocket_channels:
            ensure_ref_in_file(
                main_serverless_yml_file,
                ["functions"],
                self.handlers_yml_file,
            )
            handlers_yml = self.build_handlers_yml()
            create_yml_file(self.handlers_yml_file, handlers_yml)

        ensure_ref_in_file(
            main_serverless_yml_file,
            ["resources"],
            self.resources_yml_file,
        )
        resources_yml = self.build_resources_yml()
        create_yml_file(self.resources_yml_file, resources_yml)

        role_statement_yml = self.build_role_statement_yml()
        create_yml_file(self.role_statement_yml_file, role_statement_yml)
        for i in range(len(role_statement_yml["iamRoleStatements"])):
            ensure_ref_in_file(
                main_serverless_yml_file,
                ["provider", "iamRoleStatements"],
                self.role_statement_yml_file,
                f"iamRoleStatements.{i}",
            )

    @staticmethod
    def build_handlers_yml() -> ExternalItemType:
        handler_definitions = {
            "websockets": {
                "handler": "servey.servey_aws.lambda_websocket.lambda_handler",
                "events": [
                    {"websocket": {"route": "$connect"}},
                    {"websocket": {"route": "$disconnect"}},
                    {"websocket": {"route": "$default"}},
                ],
            }
        }
        return handler_definitions

    def build_resources_yml(self) -> ExternalItemType:
        service_name = get_servey_main()
        resources = {
            channel.name.title().replace("_", "")
            + "SQS": {
                "Type": "AWS::SQS::Queue",
                "Properties": {"QueueName": service_name + "-" + channel.name},
            }
            for channel in self.event_channels
            if isinstance(channel, BackgroundActionChannel)
        }
        if self.has_websocket_channels:
            resources[self.connection_table_name.title().replace("_", "")] = {
                "Type": "AWS::DynamoDB::Table",
                "Properties": {
                    "TableName": self.connection_table_name,
                    "BillingMode": "PAY_PER_REQUEST",
                    "AttributeDefinitions": [
                        {"AttributeName": "connection_id", "AttributeType": "S"},
                        {
                            "AttributeName": "subscription_name",
                            "AttributeType": "S",
                        },
                    ],
                    "KeySchema": [
                        {"AttributeName": "connection_id", "KeyType": "HASH"},
                        {"AttributeName": "subscription_name", "KeyType": "RANGE"},
                    ],
                    "GlobalSecondaryIndexes": [
                        {
                            "IndexName": "gsi__subscription_name__connection_id",
                            "Projection": {"ProjectionType": "ALL"},
                            "KeySchema": [
                                {
                                    "AttributeName": "subscription_name",
                                    "KeyType": "HASH",
                                },
                                {
                                    "AttributeName": "connection_id",
                                    "KeyType": "RANGE",
                                },
                            ],
                        }
                    ],
                },
            }
        resource_definitions = {"Resources": resources}
        return resource_definitions

    def build_role_statement_yml(self) -> ExternalItemType:
        role_statements = []
        if self.has_websocket_channels:
            role_statements.append(
                {
                    "Effect": "Allow",
                    "Action": [
                        "dynamodb:BatchWriteItem",
                        "dynamodb:DeleteItem",
                        "dynamodb:GetItem",
                        "dynamodb:PutItem",
                        "dynamodb:Query",
                    ],
                    "Resource": [
                        {
                            "Fn::GetAtt": [
                                self.connection_table_name.title().replace("_", ""),
                                "Arn",
                            ]
                        },
                        {
                            "Fn::Join": [
                                "/",
                                [
                                    {
                                        "Fn::GetAtt": [
                                            self.connection_table_name.title().replace(
                                                "_", ""
                                            ),
                                            "Arn",
                                        ]
                                    },
                                    "index",
                                    "gsi__subscription_name__connection_id",
                                ],
                            ]
                        },
                    ],
                }
            )

        if next(
            (
                True
                for c in self.event_channels
                if isinstance(c, BackgroundActionChannel)
            ),
            False,
        ):
            role_statements.append(
                {
                    "Effect": "Allow",
                    "Action": [
                        "sqs:SendMessage",
                        "sqs:ReceiveMessage",
                        "sqs:DeleteMessage",
                        "sqs:GetQueueUrl",
                    ],
                    "Resource": [
                        {"Fn::GetAtt": [c.name.title().replace("_", "") + "SQS", "Arn"]}
                        for c in self.event_channels
                        if isinstance(c, BackgroundActionChannel)
                    ],
                }
            )
        subscription_policy = {"iamRoleStatements": role_statements}
        return subscription_policy
