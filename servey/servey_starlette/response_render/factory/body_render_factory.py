import inspect
from abc import abstractmethod
from typing import Optional

from marshy import get_default_context

from servey2.action.finder.found_action import FoundAction
from servey2.servey_starlette.response_render.body_render import BodyRender
from servey2.servey_starlette.response_render.factory.response_render_factory_abc import ResponseRenderFactoryABC
from servey2.servey_starlette.response_render.response_render_abc import ResponseRenderABC


class BodyRenderFactory(ResponseRenderFactoryABC):
    priority: int = 50

    def create(self, action: FoundAction) -> Optional[ResponseRenderABC]:
        return_type = inspect.signature(action.fn).return_annotation
        marshaller = get_default_context().get_marshaller(return_type)
        return BodyRender(marshaller, action.action_meta.result_schema)
