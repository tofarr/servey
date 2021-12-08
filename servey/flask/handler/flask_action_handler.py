from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate
from http import HTTPStatus
import logging
from typing import Dict, Any

from flask import Flask, Request, Response, jsonify
from marshy.types import ExternalItemType

from servey.action import Action
from servey.cache.cache_header import CacheHeader
from servey.flask.handler.flask_handler_abc import FlaskHandlerABC

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FlaskActionHandler(FlaskHandlerABC):
    action: Action
    auth_cookie_name: str = 'session'

    def register(self, flask: Flask):
        logger.info(f'register_with_flask:{self.action.name}')
        flask.add_url_rule(rule=f"/{self.action.name.replace('_', '-')}",
                           endpoint=self.action.name,
                           view_func=self.invoker,
                           methods=[self.action.action_type.value])

    def invoker(self):
        from flask import request
        params = self.parse_params(request)
        return_value = self.action.callable(**params)
        response = self.render_response(request, return_value)
        return response

    def parse_params(self, request: Request) -> Dict:
        self.parse_headers(request)
        externalized_params = self.parse_externalized_params(request)
        params = self.action.params_marshaller.load(externalized_params)
        self.action.params_schema.validate(params)
        return params

    @staticmethod
    def parse_externalized_params(request: Request) -> ExternalItemType:
        if request.method in ('DELETE', 'GET', 'HEAD'):
            return {k: v for k, v in request.args.items()}
        elif request.content_type.lower() == 'application/json':
            return request.json
        else:
            return {k: v[0] for k, v in request.args.items()}

    def parse_headers(self, request: Request):
        if self.action.authorizer:
            token = request.headers.get('Authorization') or request.cookies.get(self.auth_cookie_name)
            self.action.authorizer.authorize(token)

    def render_response(self, request: Request, return_value: Any) -> Response:
        cache_header = self.action.cache_control.get_cache_header(return_value)
        if not self.is_modified(request, cache_header):
            return Response(status=HTTPStatus.NOT_MODIFIED)
        self.action.return_schema.validate(return_value)
        dumped = self.action.return_marshaller.dump(return_value)
        response = jsonify(dumped)
        response.headers.update(cache_header.get_http_headers())
        return response

    @staticmethod
    def is_modified(request: Request, cache_header: CacheHeader) -> bool:
        if_none_match = request.headers.get('If-None-Match')
        if if_none_match is not None:
            return cache_header.etag != if_none_match

        if_modified_since = request.headers.get('If-Modified-Since')
        if if_modified_since and cache_header.updated_at:
            if_modified_since = datetime(*parsedate(if_modified_since)[:6])
            return if_modified_since < cache_header.updated_at

        return True
