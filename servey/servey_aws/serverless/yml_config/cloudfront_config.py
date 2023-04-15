import os
from pathlib import Path

from marshy.types import ExternalItemType

from servey.finder.action_finder_abc import find_actions_with_trigger_type
from servey.servey_aws.serverless.yml_config.yml_config_abc import (
    YmlConfigABC,
    ensure_ref_in_file,
    create_yml_file,
)


class CloudfrontConfig(YmlConfigABC):
    """
    Set up some aspect of the serverless environment yml files. (For example, functions, resources, etc...)
    """
    static_site_directory: Path = Path(os.environ.get("SERVEY_STATIC_SITE_DIR") or "static_site")
    static_site_bucket_resource_yml_file: str = "serverless_servey/cloudfront_resource.yml"

    def configure(self, main_serverless_yml_file: str):
        has_static_site = self.static_site_directory.exists()
        has_web_page = False
        try:
            # noinspection PyUnresolvedReferences
            from servey.servey_web_page.web_page_trigger import WebPageTrigger
            has_web_page = next((True for _ in find_actions_with_trigger_type(WebPageTrigger)), False)
        except ImportError:
            pass
        if not has_static_site and not has_web_page:
            return
        # If there is a static site
        ensure_ref_in_file(
            main_serverless_yml_file,
            ["resources"],
            self.static_site_bucket_resource_yml_file,
        )
        cloudfront_resource_yml = self.build_cloudfront_resource_yml()
        create_yml_file(
            self.static_site_bucket_resource_yml_file, cloudfront_resource_yml
        )

    @staticmethod
    def build_cloudfront_resource_yml() -> ExternalItemType:
        static_site_bucket_resource = {
            "Resources": {
                "End2EndIndexFn": {
                    "Type": "AWS::CloudFront::Function",
                    "Properties": {
                        "Name": "End2EndIndexFn",
                        "AutoPublish": True,
                        "FunctionConfig": {
                            "Comment": "Add index.html when path ends with /",
                            "Runtime": "cloudfront-js-1.0"
                        },
                        "FunctionCode": "\n".join((
                            "function handler(event) {",
                            "    var request = event.request;",
                            "    var uri = request.uri;",
                            "",
                            "    if (uri.endsWith('/')) {",
                            "        request.uri += 'index.html';",
                            "    }",
                            "    else if (!uri.includes('.')) {",
                            "        request.uri += '/index.html';",
                            "    }",
                            "",
                            "    return request;",
                            "}",
                            ""
                        ))
                    }
                },
                "End2EndDistribution": {
                    "Type": "AWS::CloudFront::Distribution",
                    "Properties": {
                        "DistributionConfig": {
                            "Enabled": "true",
                            "DefaultRootObject": "/",
                            "DefaultCacheBehavior": {
                                "AllowedMethods": [
                                    "GET",
                                    "HEAD"
                                ],
                                "MinTTL": "0",
                                "MaxTTL": "0",
                                "DefaultTTL": "0",
                                "TargetOriginId": "s3Origin",
                                "ForwardedValues": {
                                    "QueryString": "false"
                                },
                                "ViewerProtocolPolicy": "redirect-to-https",
                                "FunctionAssociations": [
                                    {
                                        "EventType": "viewer-request",
                                        "FunctionARN": {
                                            "Ref": "End2EndIndexFn"
                                        }
                                    }
                                ]
                            },
                            "CacheBehaviors": [
                                {
                                    "AllowedMethods": [
                                        "HEAD",
                                        "DELETE",
                                        "POST",
                                        "GET",
                                        "OPTIONS",
                                        "PUT",
                                        "PATCH"
                                    ],
                                    "TargetOriginId": "apiGatewayAPIOrigin",
                                    "ForwardedValues": {
                                        "QueryString": True,
                                        "Cookies": {
                                            "Forward": "all"
                                        }
                                    },
                                    "ViewerProtocolPolicy": "https-only",
                                    "MinTTL": "0",
                                    "MaxTTL": "6",
                                    "DefaultTTL": "3",
                                    "PathPattern": "actions/*"
                                },
                                {
                                    "AllowedMethods": [
                                        "HEAD",
                                        "DELETE",
                                        "POST",
                                        "GET",
                                        "OPTIONS",
                                        "PUT",
                                        "PATCH"
                                    ],
                                    "TargetOriginId": "appsyncAPIOrigin",
                                    "ForwardedValues": {
                                        "QueryString": False,
                                        "Cookies": {
                                            "Forward": "all"
                                        }
                                    },
                                    "ViewerProtocolPolicy": "https-only",
                                    "MinTTL": "0",
                                    "MaxTTL": "6",
                                    "DefaultTTL": "3",
                                    "PathPattern": "graphql"
                                }
                            ],
                            "Origins": [
                                {
                                    "DomainName": {
                                        "Fn::Join": [
                                            "",
                                            [
                                                {
                                                    "Ref": "ApiGatewayRestApi"
                                                },
                                                ".execute-api.${self:provider.region}.amazonaws.com"
                                            ]
                                        ]
                                    },
                                    "Id": "apiGatewayAPIOrigin",
                                    "OriginPath": "/${self:provider.stage}",
                                    "CustomOriginConfig": {
                                        "OriginProtocolPolicy": "https-only"
                                    }
                                },
                                {
                                    "DomainName": {
                                        "Fn::Select": [
                                            0,
                                            {
                                                "Fn::Split": [
                                                    "/graphql",
                                                    {
                                                        "Fn::Select": [
                                                            1,
                                                            {
                                                                "Fn::Split": [
                                                                    "https://",
                                                                    {
                                                                        "Fn::GetAtt": [
                                                                            "GraphQlApi",
                                                                            "GraphQLUrl"
                                                                        ]
                                                                    }
                                                                ]
                                                            }
                                                        ]
                                                    }
                                                ]
                                            }
                                        ]
                                    },
                                    "Id": "appsyncAPIOrigin",
                                    "CustomOriginConfig": {
                                        "OriginProtocolPolicy": "https-only"
                                    }
                                },
                                {
                                    "DomainName": "${self:custom.staticBucket}.s3.amazonaws.com",
                                    "Id": "s3Origin",
                                    "S3OriginConfig": {
                                        "OriginAccessIdentity": {
                                            "Fn::Join": [
                                                "",
                                                [
                                                    "origin-access-identity/cloudfront/",
                                                    {
                                                        "Ref": "OriginAccessIdentity"
                                                    }
                                                ]
                                            ]
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }
        return static_site_bucket_resource
