import json
from dataclasses import dataclass
from http import HTTPStatus
from typing import Iterable

from old.handler.action_handler import ActionHandler
from old.handler.handler_abc import HandlerABC
from old.request import Request
from old.response import Response


@dataclass(frozen=True)
class MetaHandler(HandlerABC):
    action_handlers: Iterable[ActionHandler]

    def match(self, request: Request) -> bool:
        return request.method in ['GET', 'OPTIONS'] and request.path[-1] == 'meta'

    def handle_request(self, request: Request) -> Response:
        content = []
        for action_handler in self.action_handlers:
            content_meta = dict(
                name=action_handler.name,
                params_schema=action_handler.params_schema.to_json_schema(),
                return_schema=action_handler.return_schema.to_json_schema()
            )
            if action_handler.doc:
                content_meta['doc'] = action_handler.doc.strip()
            content.append(content_meta)
        return Response(HTTPStatus.OK, content=json.dumps(content))
