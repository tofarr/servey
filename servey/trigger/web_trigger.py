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
