from dataclasses import dataclass
from typing import Any

from marshy import ExternalType
from marshy.marshaller.marshaller_abc import MarshallerABC

from servey2.servey_aws.result_render.result_render_abc import ResultRenderABC


@dataclass
class ResultRender(ResultRenderABC):
    marshaller: MarshallerABC

    def render_result(self, result: Any) -> ExternalType:
        dumped = self.marshaller.dump(result)
        return dumped
