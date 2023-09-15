from dataclasses import dataclass, field
from http.client import HTTPException
from typing import Optional, Any, Dict

from marshy.types import ExternalItemType
from starlette.responses import Response, RedirectResponse

from servey.servey_starlette.action_endpoint.action_endpoint import ActionEndpoint
from servey.servey_web_page.redirect import Redirect
from servey.servey_web_page.web_page_response import WebPageResponse
from servey.servey_web_page.web_page_trigger import get_environment


@dataclass
class WebPageActionEndpoint(ActionEndpoint):
    """
    Wrapper that combines an action with a template
    """

    template_name: Optional[str] = None
    response_headers: Dict[str, str] = field(
        default_factory=lambda: {"Content-Type": "text/html"}
    )

    def __post_init__(self):
        if not self.template_name:
            self.template_name = f"{self.action.name}.j2"

    def render_response(self, result: Any):
        if isinstance(result, Redirect):
            return RedirectResponse(result.url, result.status_code)
        if not isinstance(result, WebPageResponse):
            result = WebPageResponse(result, headers=self.response_headers)
        result_content = (
            self.result_marshaller.dump(result.model)
            if self.result_marshaller
            else None
        )
        if self.result_schema:
            error = next(self.result_schema.iter_errors(result_content), None)
            if error:
                raise HTTPException(500, str(error))
        body = self.template.render(model=result_content)

        return Response(content=body, headers=result.headers)

    @property
    def template(self):
        template = getattr(self, "_template", None)
        if not template:
            template = get_environment().get_template(self.template_name)
            setattr(self, "_template", template)
        return template

    def to_openapi_schema(self, schema: ExternalItemType):
        pass  # Not included in OpenAPI
