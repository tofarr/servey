import json
from dataclasses import dataclass
from typing import Any, Optional, Dict

import boto3
from marshy.marshaller.marshaller_abc import MarshallerABC
from schemey import Schema

from servey.access_control.authorization import Authorization
from servey.access_control.authorizer_abc import AuthorizerABC
from servey.servey_error import ServeyError


@dataclass
class LambdaCall:
    """Action which Executes a remote lambda."""

    lambda_name: str
    param_schema: Schema
    param_marshaller: MarshallerABC
    result_schema: Schema
    result_marshaller: MarshallerABC
    authorizer: Optional[AuthorizerABC] = None
    authorization_arg: Optional[str] = None
    client: Optional[Any] = None

    def __post_init__(self):
        if not self.client:
            self.client = boto3.client("lambda")

    def __call__(self, **kwargs) -> Any:
        result = self.client.execute(
            FunctionName=self.lambda_name,
            # ClientContext
            Payload=self.create_payload(kwargs),
        )
        result_payload = result.get("Payload")
        if result_payload:
            result_payload = json.loads(result_payload)
        status_code = result["StatusCode"]
        if status_code != 200:
            raise ServeyError(result_payload)
        self.result_schema.validate(result_payload)
        result_payload = self.result_marshaller.load(result_payload)
        return result_payload

    def execute_async(self, authorization: Authorization, **kwargs) -> Any:
        self.client.execute(
            FunctionName=self.lambda_name,
            InvocationType="Event",
            # ClientContext
            Payload=self.create_payload(authorization, kwargs),
        )

    def create_payload(self, kwargs: Dict[str, Any]) -> str:
        authorization = None
        if self.authorization_arg:
            authorization = kwargs.pop(self.authorization_arg, None)
            authorization = self.authorizer.encode(authorization)
        params = self.param_marshaller.dump(kwargs)
        self.param_schema.validate(params)
        payload = dict(params=params)
        if authorization:
            payload["authorization"] = authorization
        dumped = json.dumps(payload)
        return dumped
