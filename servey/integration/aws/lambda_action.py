import json
from dataclasses import dataclass
from typing import Any, Optional

import boto3
from marshy.marshaller.marshaller_abc import MarshallerABC

from servey.access_control.action_access_control_abc import ActionAccessControlABC
from servey.access_control.allow_all import ALLOW_ALL
from servey.access_control.authorization import Authorization
from servey.action_abc import ActionABC
from servey.servey_error import ServeyError


@dataclass
class LambdaAction(ActionABC):
    """ Action which invokes a remote lambda. """

    lambda_name: str
    param_marshaller: MarshallerABC
    result_marshaller: MarshallerABC
    access_control: ActionAccessControlABC = ALLOW_ALL
    client: Optional[Any] = None

    def __post_init__(self):
        if not self.client:
            self.client = boto3.client('lambda')

    def invoke(self, authorization: Authorization, **kwargs) -> Any:
        self.check_auth(authorization)
        params = self.param_marshaller.dump(kwargs)
        result = self.client.invoke(
            FunctionName=self.lambda_name,
            # ClientContext
            Payload=json.dumps(params)
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
        self.check_auth(authorization)
        params = self.param_marshaller.dump(kwargs)
        self.client.invoke(
            FunctionName=self.lambda_name,
            InvocationType='Event',
            # ClientContext
            Payload=json.dumps(params)
        )

    def check_auth(self, authorization: Authorization):
        """
        Checking the authorization on this end - nothing stops the lambda from checking it too. (As it should)
        Typically, the aws context will have its own implementation of this.
        Checking on this end means that we don't have to implement anything unusual in he lambda security - the
        lambda on the other end does not need to use this framework.
        """
        if not self.access_control.is_executable(authorization):
            raise ServeyError('insufficent_permissions')
