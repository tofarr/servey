from marshy.types import ExternalItemType

from servey.servey_aws.serverless.yml_config.yml_config_abc import (
    YmlConfigABC,
    ensure_ref_in_file,
    create_yml_file,
)


class KmsKeyConfig(YmlConfigABC):
    """
    Set up some aspect of the serverless environment yml files. (For example, functions, resources, etc...)
    """

    kms_resource_yml_file: str = "serverless_servey/kms_resource.yml"
    kms_role_statement_yml_file: str = "serverless_servey/kms_role_statement.yml"

    def configure(self, main_serverless_yml_file: str):
        ensure_ref_in_file(
            main_serverless_yml_file,
            ["resources"],
            self.kms_resource_yml_file,
        )
        ensure_ref_in_file(
            main_serverless_yml_file,
            ["provider", "iamRoleStatements"],
            self.kms_role_statement_yml_file,
            "iamRoleStatements.0",
        )
        kms_resource_yml = self.build_kms_resource_yml()
        create_yml_file(
            self.kms_resource_yml_file, kms_resource_yml, _mutate_kms_resource_str
        )
        kms_role_statement_yml = self.build_kms_role_statement_yml()
        create_yml_file(self.kms_role_statement_yml_file, kms_role_statement_yml)

    @staticmethod
    def build_kms_resource_yml() -> ExternalItemType:
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


def _mutate_kms_resource_str(kms_resource: str) -> str:
    kms_resource = kms_resource.replace(
        "AWS_ACCOUNT_ID", "!Sub arn:aws:iam::${aws:accountId}:root"
    )
    kms_resource = kms_resource.replace("SERVEY_KMS_KEY", "!Ref serveyKmsKey")
    return kms_resource
