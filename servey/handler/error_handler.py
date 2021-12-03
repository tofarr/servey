from dataclasses import dataclass
from http import HTTPStatus

from servey.handler.handler_abc import HandlerABC
from servey.request import Request
from servey.response import Response


@dataclass
class ErrorHandler(HandlerABC):

    def match(self, request: Request) -> bool:
        return True

    def handle_request(self, request: Request) -> Response:
        return Response(HTTPStatus.INTERNAL_SERVER_ERROR)
