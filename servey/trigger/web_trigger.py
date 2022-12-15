from dataclasses import dataclass
from enum import Enum


class WebTriggerMethod(Enum):
    DELETE = "delete"
    GET = "get"
    HEAD = "head"
    OPTIONS = "options"
    PATCH = "patch"
    POST = "post"
    PUT = "put"


@dataclass(frozen=True)
class WebTrigger:
    method: WebTriggerMethod = WebTriggerMethod.POST


WEB_GET = WebTrigger(WebTriggerMethod.GET)
WEB_POST = WebTrigger(WebTriggerMethod.POST)
BODY_METHODS = (
    WebTriggerMethod.PATCH,
    WebTriggerMethod.POST,
    WebTriggerMethod.PUT,
)
UPDATE_METHODS = (
    WebTriggerMethod.DELETE,
    WebTriggerMethod.PATCH,
    WebTriggerMethod.POST,
    WebTriggerMethod.PUT,
)
