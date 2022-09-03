from dataclasses import dataclass
from typing import Any

from marshy import ExternalType
from schemey import Schema

from servey.servey_aws.result_render.result_render_abc import ResultRenderABC


@dataclass
class ValidatingResultRender(ResultRenderABC):
    result_render: ResultRenderABC
    schema: Schema

    def render_result(self, result: Any) -> ExternalType:
        result = self.result_render.render_result(result)
        self.schema.validate(result)
        return result
