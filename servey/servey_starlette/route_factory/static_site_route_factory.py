import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles

from servey.servey_starlette.route_factory.route_factory_abc import RouteFactoryABC


@dataclass
class StaticSiteRouteFactory(RouteFactoryABC):
    priority: int = 80
    path: str = "/"
    directory: Path = Path(os.environ.get("SERVEY_STATIC_SITE_DIR") or "static_site")

    def create_routes(self) -> Iterator[Route]:
        if self.directory.exists():
            yield Mount(
                self.path,
                app=StaticFiles(directory=self.directory, html=True),
                name="static_site",
            )
