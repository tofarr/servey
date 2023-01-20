from dataclasses import dataclass
from http.client import HTTPException
from typing import Optional, Any

from jinja2 import Environment, PackageLoader
from starlette.responses import HTMLResponse

from servey.servey_starlette.action_endpoint.action_endpoint import ActionEndpoint
from servey.servey_web_page.web_page_trigger import get_environment
from servey.util import get_servey_main


@dataclass
class WebPageActionEndpoint(ActionEndpoint):
    """
    Wrapper that combines an action with a template
    """

    template_name: Optional[str] = None

    def __post_init__(self):
        if not self.template_name:
            self.template_name = f"{self.action.name}.j2"

    def render_response(self, result: Any):
        result_content = (
            self.result_marshaller.dump(result) if self.result_marshaller else None
        )
        if self.result_schema:
            error = next(self.result_schema.iter_errors(result_content), None)
            if error:
                raise HTTPException(500, str(error))
        body = self.template.render(model=result_content)
        return HTMLResponse(body)

    @property
    def template(self):
        template = getattr(self, "_template", None)
        if not template:
            template = get_environment().get_template(self.template_name)
            setattr(self, "_template", template)
        return template
