from dataclasses import dataclass
from typing import Any

from starlette.responses import JSONResponse

from servey.action import Action
from servey.executor import Executor
from servey.integration.aws.render.result_render_abc import ResultRenderABC


@dataclass
class ResultRender(ResultRenderABC):
    action: Action

    def render(self, executor: Executor, result: Any) -> JSONResponse:
        action_meta = self.action.action_meta
        dumped = action_meta.result_marshaller.dump(result)
        action_meta.result_schema.validate(dumped)
        return dumped
