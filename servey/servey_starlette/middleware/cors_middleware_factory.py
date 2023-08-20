from dataclasses import dataclass, field
from typing import Optional, List

from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from servey.cors import get_allowed_origins
from servey.servey_starlette.middleware.middleware_factory_abc import (
    MiddlewareFactoryABC,
)


@dataclass
class CORSMiddlewareFactory(MiddlewareFactoryABC):
    allow_origins: List[str] = field(default_factory=get_allowed_origins)

    def create(self) -> Optional[Middleware]:
        if self.allow_origins:
            return Middleware(
                CORSMiddleware,
                allow_origins=self.allow_origins,
                allow_methods="*",
                allow_headers="*",
                allow_credentials=True,
            )
