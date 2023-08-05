import logging

from marshy.factory.impl_marshaller_factory import get_impls
from starlette.applications import Starlette

from servey.servey_starlette.middleware.middleware_factory_abc import (
    MiddlewareFactoryABC,
)
from servey.servey_starlette.route_factory.route_factory_abc import RouteFactoryABC

LOGGER = logging.getLogger(__name__)
routes = []
for route_factory in sorted(
    list(get_impls(RouteFactoryABC)), key=lambda f: f.priority, reverse=True
):
    routes.extend(route_factory().create_routes())
for route in routes:
    LOGGER.debug("starlette_path:%s", route.path)

middleware = [
    f
    for f in (
        f.create()
        for f in sorted(
            [f() for f in get_impls(MiddlewareFactoryABC)],
            key=lambda f: f.priority,
            reverse=True,
        )
    )
    if f
]
app = Starlette(routes=routes, middleware=middleware)
