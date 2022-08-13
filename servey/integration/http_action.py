from dataclasses import dataclass
from typing import Any, Optional
from urllib.parse import urlencode
import requests

from marshy.marshaller.marshaller_abc import MarshallerABC

from servey.access_control.authorization import Authorization
from servey.access_control.authorizer_abc import AuthorizerABC
from servey.action_abc import ActionABC


@dataclass
class HttpAction(ActionABC):
    """ Remote invocation of an action over http. """
    url: str
    param_marshaller: MarshallerABC
    result_marshaller: MarshallerABC
    method: str = "POST"
    authorizer: Optional[AuthorizerABC] = None

    def invoke(self, authorization: Authorization, params: Dict[str, Any]) -> Any:
        response = self.get_response(authorization, kwargs)
        result = response.json
        result = self.result_marshaller.load(result)
        return result

    def invoke_async(self, authorization: Authorization, **kwargs):
        self.get_response(authorization, kwargs)

    def get_response(self, authorization: Authorization, kwargs) -> Any:
        params = self.param_marshaller.dump(kwargs)
        if self.method == 'GET':
            return requests.get(f"{self.url}?{urlencode(params)}", auth=self.auth_to_header(authorization))
        else:
            return requests.post(self.url, auth=self.auth_to_header(authorization), json=params)

    def auth_to_header(self, authorization: Authorization) -> Optional[str]:
        """ Convert the authorization given to a header """
        if self.authorizer:
            return self.authorizer.encode(authorization)
