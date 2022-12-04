from datetime import datetime
from io import StringIO

from marshy.types import ExternalItemType
from ruamel.yaml import YAML

from servey.servey_aws.serverless.yml_config.yml_config_abc import (
    YmlConfigABC,
    ensure_ref_in_file,
    GENERATED_HEADER,
)


class KmsKeyConfig(YmlConfigABC):
    """
    Set up some aspect of the serverless environment yml files. (For example, functions, resources, etc...)
    """

    servey_kms_resource_yml_file: str = "serverless_kms_resource.yml"
    servey_kms_role_statement_yml_file: str = "serverless_kms_role_statement.yml"

    def configure(self, main_serverless_yml_file: str):
        ensure_ref_in_file(
            main_serverless_yml_file,
            ["resources"],
            self.servey_kms_resource_yml_file,
        )
        ensure_ref_in_file(
            main_serverless_yml_file,
            ["provider", "iamRoleStatements"],
            self.servey_kms_role_statement_yml_file,
            "iamRoleStatements.0",
        )
        self.build_kms_resource_functions_yml_file()
        self.build_kms_role_statement_yml_file()

    def build_kms_resource_functions_yml_file(self):
        kms_resource_functions_yml = self.build_kms_resource_functions_yml()
        with open(self.servey_kms_resource_yml_file, "w") as writer:
            writer.write("# ")
            writer.write(GENERATED_HEADER.replace("\n", "\n# "))
            writer.write(f"\n# Updated at: {datetime.now().isoformat()}\n\n")
            yaml = YAML()
            s = StringIO()
            yaml.dump(kms_resource_functions_yml, s)
            s = s.getvalue().replace(
                "AWS_ACCOUNT_ID", "!Sub arn:aws:iam::${aws:accountId}:root"
            )
            s = s.replace("SERVEY_KMS_KEY", "!Ref serveyKmsKey")
            writer.write(s)

    @staticmethod
    def build_kms_resource_functions_yml() -> ExternalItemType:
        kms_resource = {
            "Resources": {
                "serveyKmsKey": {
                    "Type": "AWS::KMS::Key",
                    "Properties": {
                        "Description": "Key used for servey authentication and authorization",
                        "Enabled": True,
                        "KeySpec": "RSA_4096",
                        "KeyUsage": "SIGN_VERIFY",
                        "KeyPolicy": {
                            "Version": "2012-10-17",
                            "Id": "serveyKmsKey",
                            "Statement": {
                                "Sid": "Allow administration of the key",
                                "Effect": "Allow",
                                "Principal": {
                                    "AWS": "AWS_ACCOUNT_ID",
                                },
                                "Action": "kms:*",
                                "Resource": "*",
                            },
                        },
                    },
                },
                "serveyKmsKeyAlias": {
                    "Type": "AWS::KMS::Alias",
                    "Properties": {
                        "AliasName": "alias/serveyKmsKey",
                        "TargetKeyId": "SERVEY_KMS_KEY",
                    },
                },
            },
        }
        return kms_resource

    def build_kms_role_statement_yml_file(self):
        kms_role_statement_yml = self.build_kms_role_statement_yml()
        with open(self.servey_kms_role_statement_yml_file, "w") as writer:
            writer.write("# ")
            writer.write(GENERATED_HEADER.replace("\n", "\n# "))
            writer.write(f"\n# Updated at: {datetime.now().isoformat()}\n\n")
            yaml = YAML()
            s = StringIO()
            yaml.dump(kms_role_statement_yml, s)
            s = s.getvalue()
            writer.write(s)

    @staticmethod
    def build_kms_role_statement_yml() -> ExternalItemType:
        kms_policy = {
            "iamRoleStatements": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "kms:Sign",
                        "kms:Verify",
                        "kms:GetPublicKey",
                    ],
                    "Resource": {
                        "Fn::GetAtt": [
                            "serveyKmsKey",
                            "Arn",
                        ]
                    },
                }
            ]
        }
        return kms_policy
