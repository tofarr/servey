import os
from pathlib import Path
from random import randint

from marshy.types import ExternalItemType
from ruamel.yaml import YAML

from servey.servey_aws.serverless.yml_config.yml_config_abc import (
    YmlConfigABC,
    ensure_ref_in_file,
    create_yml_file,
)

ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyz'


class StaticSiteBucketConfig(YmlConfigABC):
    """
    Set up some aspect of the serverless environment yml files. (For example, functions, resources, etc...)
    """
    static_site_directory: Path = Path(os.environ.get("SERVEY_STATIC_SITE_DIR") or "static_site")
    static_site_bucket_resource_yml_file: str = "serverless_servey/static_site_bucket_resource.yml"

    def configure(self, main_serverless_yml_file: str):
        if not self.static_site_directory.exists():
            return
        # If there is a static site
        ensure_ref_in_file(
            main_serverless_yml_file,
            ["resources"],
            self.static_site_bucket_resource_yml_file,
        )
        self.add_custom_bucket_yml(main_serverless_yml_file)
        static_site_bucket_resource_yml = self.build_static_site_bucket_resource_yml()
        create_yml_file(
            self.static_site_bucket_resource_yml_file, static_site_bucket_resource_yml
        )

    def add_custom_bucket_yml(self, main_serverless_yml_file: str):
        yaml = YAML()
        with open(main_serverless_yml_file, "r") as reader:
            root = yaml.load(reader)
            custom = root.get('custom')
            static_bucket = custom.get('staticBucket')
            if static_bucket:
                return static_bucket
        static_bucket = 'b' + ''.join(ALPHABET[randint(0, 35)] for _ in range(10))
        custom['staticBucket'] = static_bucket
        custom['s3Sync'] = [{
            'bucketName': '${self: custom.staticBucket}',
            'localDir': self.static_site_directory
        }]
        root['plugins'].append('serverless-s3-sync')
        with open(main_serverless_yml_file, "w") as writer:
            yaml.dump(root, writer)
        return static_bucket

    @staticmethod
    def build_static_site_bucket_resource_yml() -> ExternalItemType:
        static_site_bucket_resource = {
            "Resources": {
                "OriginAccessIdentity": {
                    "Type": "AWS::CloudFront::CloudFrontOriginAccessIdentity",
                    "Properties": {
                        "CloudFrontOriginAccessIdentityConfig": {
                            "Comment": "Allow cloudfront to access the static bucket"
                        }
                    }
                },
                "StaticBucket": {
                    "Type": "AWS::S3::Bucket",
                    "Properties": {
                        "AccessControl": "Private",
                        "BucketName": "${self:custom.staticBucket}",
                        "WebsiteConfiguration": {
                            "IndexDocument": "index.html"
                        }
                    }
                },
                "StaticSiteS3BucketPolicy": {
                    "Type": "AWS::S3::BucketPolicy",
                    "Properties": {
                        "Bucket": {
                            "Ref": "StaticBucket"
                        },
                        "PolicyDocument": {
                            "Statement": [
                                {
                                    "Sid": "AllowCloudFrontServicePrincipalReadOnly",
                                    "Effect": "Allow",
                                    "Principal": {
                                        "AWS": {
                                            "Fn::Join": [
                                                "",
                                                [
                                                    "arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity ",
                                                    {
                                                        "Ref": "OriginAccessIdentity"
                                                    }
                                                ]
                                            ]
                                        }
                                    },
                                    "Action": [
                                        "s3:GetObject"
                                    ],
                                    "Resource": {
                                        "Fn::Join": [
                                            "",
                                            [
                                                "arn:aws:s3:::",
                                                {
                                                    "Ref": "StaticBucket"
                                                },
                                                "/*"
                                            ]
                                        ]
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }
        return static_site_bucket_resource
