import json
from dataclasses import dataclass
from typing import Any

from marshy import ExternalType
from marshy.marshaller.marshaller_abc import MarshallerABC

from servey.servey_aws.result_render.result_render_abc import ResultRenderABC


@dataclass
class ResultRender(ResultRenderABC):
    marshaller: MarshallerABC

    def render(self, result: Any) -> ExternalType:
        dumped = self.marshaller.dump(result)
        return dumped
