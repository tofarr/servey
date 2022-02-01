from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate
from http import HTTPStatus
from typing import Optional, Dict, Any

from marshy.types import ExternalItemType
from starlette.formparsers import MultiPartParser, FormParser
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

from servey.action import Action
from servey.cache.cache_header import CacheHeader
from servey.json_params import from_params


@dataclass(frozen=True)
class StarletteActionHandler:
    action: Action
    auth_header: Optional[str] = None

    async def handle(self, request):
        params = await self.parse_params(request)
        return_value = self.action.callable(**params)
        response = self.create_response(request, return_value)
        return response

    async def parse_params(self, request: Request) -> Dict:
        self.parse_headers(request)
        externalized_params = await self.parse_externalized_params(request)
        externalized_params.update(request.path_params)
        params = self.action.params_marshaller.load(externalized_params)
        self.action.params_schema.validate(params)
        return params

    def parse_headers(self, request: Request):
        if self.auth_header:
            auth_token = request.headers.get(self.auth_header)
            self.action.authorizer.authorize(auth_token)

    @staticmethod
    async def parse_externalized_params(request: Request) -> ExternalItemType:
        content_type = (request.headers.get("Content-Type") or '').lower()
        if content_type == "application/json":
            content = await request.json()
            return content
        if content_type == "multipart/form-data":
            multipart_parser = MultiPartParser(request.headers, request.stream())
            form = await multipart_parser.parse()
        elif content_type == "application/x-www-form-urlencoded":
            form_parser = FormParser(request.headers, request.stream())
            form = await form_parser.parse()
        else:
            form = request.query_params
        params = iter(form.multi_items())
        content = from_params(params)
        return content

    def create_response(self, request, return_value: Any) -> Response:
        cache_header = self.action.cache_control.get_cache_header(return_value)
        if not self.is_modified(request, cache_header):
            return Response(status_code=HTTPStatus.NOT_MODIFIED)
        self.action.return_schema.validate(return_value)
        dumped = self.action.return_marshaller.dump(return_value)
        response = JSONResponse(dumped)
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
