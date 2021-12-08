from dataclasses import dataclass
from http import HTTPStatus

from old.handler.handler_abc import HandlerABC
from old.request import Request
from old.response import Response


@dataclass
class NotFoundHandler(HandlerABC):

    def match(self, request: Request) -> bool:
        return True

    def handle_request(self, request: Request) -> Response:
        return Response(HTTPStatus.NOT_FOUND)
