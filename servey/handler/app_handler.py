import re
from dataclasses import dataclass
import logging
from typing import Iterable, Any

from servey.handler.action_handler import STARTS_WITH_UNDERSCORE, generate_action_handlers
from servey.handler.error_handler import ErrorHandler
from servey.handler.handler_abc import HandlerABC
from servey.handler.meta_handler import MetaHandler
from servey.handler.not_found_handler import NotFoundHandler
from servey.request import Request
from servey.response import Response

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AppHandler(HandlerABC):
    handlers: Iterable[HandlerABC]
    error_handler: HandlerABC = ErrorHandler()
    not_found_handler: HandlerABC = NotFoundHandler()

    def match(self, request: Request) -> bool:
        matched = next((True for h in self.handlers if h.match(request)), False)
        return matched

    def handle_request(self, request: Request) -> Response:
        handler = next((h for h in self.handlers if h.match(request)), self.not_found_handler)
        try:
            response = handler.handle_request(request)
            return response
        except (Exception, ValueError) as e:
            logger.error(e)
            response = self.error_handler.handle_request(request)
            return response


def app_handler(app_object: Any,
                include_meta: bool = True,
                exclude_functions: Iterable[re.Pattern] = (STARTS_WITH_UNDERSCORE,)):
    handlers = list(generate_action_handlers(app_object, exclude_functions))
    if include_meta:
        handlers.append(MetaHandler(tuple(handlers)))
    return AppHandler(handlers)


def merged_app_handler(*args: HandlerABC) -> AppHandler:
    args = list(a for a in args if a is not None)
    args.sort(key=lambda h: h.priority) # Sort so higher priority processed after lower
    handlers = []
    error_handler = ErrorHandler()
    not_found_handler = NotFoundHandler()
    for a in args:
        if a is None:
            continue
        if hasattr(a, 'handlers'):
            handlers.extend(a.handlers)
        else:
            handlers.append(a)
        if hasattr(a, 'error_handler'):
            error_handler = a.error_handler
        if hasattr(a, 'not_found_handler'):
            not_found_handler = a.not_found_handler
    handlers.sort(key=lambda h: h.priority, reverse=True) # sort so higher priority first
    return AppHandler(handlers, error_handler, not_found_handler)
