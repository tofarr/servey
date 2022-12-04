import json
from dataclasses import dataclass
from typing import Any

from marshy.marshaller.marshaller_abc import MarshallerABC
from marshy.types import ExternalItemType

from servey.servey_aws.result_render.result_render_abc import ResultRenderABC


@dataclass
class ApiGatewayResultRender(ResultRenderABC):
    marshaller: MarshallerABC

    def render(self, result: Any) -> ExternalItemType:
        # TODO: Caching headers here?
        dumped = json.dumps(self.marshaller.dump(result))
        response = {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": dumped,
        }
        return response
