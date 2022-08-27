from marshy.factory.impl_marshaller_factory import get_impls
from starlette.applications import Starlette

from servey.integration.starlette_integ.route_factory.route_factory_abc import (
    RouteFactoryABC,
)

routes = []
for route_factory in get_impls(RouteFactoryABC):
    routes.extend(route_factory().create_routes())
app = Starlette(routes=routes)
