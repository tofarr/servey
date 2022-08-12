import json
from dataclasses import dataclass
from typing import Any, Optional, Dict

import boto3
from marshy.marshaller.marshaller_abc import MarshallerABC

from servey.access_control.authorization import Authorization
from servey.action_abc import ActionABC
from servey.servey_error import ServeyError


@dataclass
class LambdaAction(ActionABC):
    """ Action which invokes a remote lambda. """

    lambda_name: str
    param_marshaller: MarshallerABC
    result_marshaller: MarshallerABC
    client: Optional[Any] = None

    def __post_init__(self):
        if not self.client:
            self.client = boto3.client('lambda')

    def invoke(self, authorization: Authorization, **kwargs) -> Any:
        result = self.client.invoke(
            FunctionName=self.lambda_name,
            # ClientContext
            Payload=self.create_payload(authorization, kwargs)
        )
        result_payload = result.get('Payload')
        if result_payload:
            result_payload = json.loads(result_payload)
        status_code = result['StatusCode']
        if status_code != 200:
            raise ServeyError(result_payload)
        result_payload = self.result_marshaller.load(result_payload)
        return result_payload

    def invoke_async(self, authorization: Authorization, **kwargs) -> Any:
        self.client.invoke(
            FunctionName=self.lambda_name,
            InvocationType='Event',
            # ClientContext
            Payload=self.create_payload(authorization, kwargs)
        )

    def create_payload(self, authorization: Authorization, kwargs: Dict[str, Any]) -> str:
        params = self.param_marshaller.dump(kwargs)
        payload = dict(
            authorization=self.encode_authorization(authorization),
            params=params
        )
        dumped = json.dumps(payload)
        return dumped
