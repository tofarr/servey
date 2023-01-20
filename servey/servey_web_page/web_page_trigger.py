from dataclasses import dataclass
from typing import Optional

from jinja2 import Environment, PackageLoader

from servey.trigger.trigger_abc import TriggerABC
from servey.trigger.web_trigger import WebTriggerMethod
from servey.util import get_servey_main


@dataclass(frozen=True)
class WebPageTrigger(TriggerABC):
    method: WebTriggerMethod = WebTriggerMethod.GET
    path: Optional[str] = None
    template_name: Optional[str] = None


def get_environment() -> Environment:
    environment = Environment(
        loader=PackageLoader(get_servey_main(), "templates"),
        auto_reload=False,  # Uvicorn handles this
    )
    environment.cache = {}
    return environment


PAGE_GET = WebPageTrigger()
