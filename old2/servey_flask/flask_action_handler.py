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
from old2.servey_flask.flask_handler_abc import FlaskHandlerABC

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
                           methods=[m.value for m in self.action.http_methods])

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
