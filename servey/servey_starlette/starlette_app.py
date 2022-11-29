import logging

from marshy.factory.impl_marshaller_factory import get_impls
from starlette.applications import Starlette

from servey.servey_starlette.route_factory.route_factory_abc import RouteFactoryABC

LOGGER = logging.getLogger(__name__)
routes = []
for route_factory in get_impls(RouteFactoryABC):
    routes.extend(route_factory().create_routes())
for route in routes:
    LOGGER.debug(f"starlette_path:%s", route.path)

app = Starlette(routes=routes)
