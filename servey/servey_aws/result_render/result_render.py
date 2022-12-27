from dataclasses import dataclass
from typing import Any, Optional

from marshy import ExternalType
from marshy.marshaller.marshaller_abc import MarshallerABC
from schemey import Schema

from servey.servey_aws.result_render.result_render_abc import ResultRenderABC


@dataclass
class ResultRender(ResultRenderABC):
    marshaller: MarshallerABC
    schema: Optional[Schema] = None

    def render(self, result: Any) -> ExternalType:
        dumped = self.marshaller.dump(result)
        if self.schema:
            self.schema.validate(dumped)
        return dumped
