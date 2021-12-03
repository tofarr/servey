import logging
from dataclasses import dataclass
from logging import Logger

from servey.handler.handler_abc import HandlerABC
from servey.request import Request
from servey.response import Response


@dataclass(frozen=True)
class ErrorHandler(HandlerABC):
    handler: HandlerABC
    logger: Logger = logging.getLogger(__name__)

    def match(self, request: Request) -> bool:
        matched = self.handler.match(request)
        return matched

    def handle_request(self, request: Request) -> Response:
        self.logger.info(f'REQUEST:{request}')
        self.handler.handle_request(request)
