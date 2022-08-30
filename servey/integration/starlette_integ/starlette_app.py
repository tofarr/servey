import logging
import os

from marshy.factory.impl_marshaller_factory import get_impls
from starlette.applications import Starlette

from servey.integration.starlette_integ.route_factory.route_factory_abc import (
    RouteFactoryABC,
)

LOGGER = logging.getLogger(__name__)
routes = []
for route_factory in get_impls(RouteFactoryABC):
    routes.extend(route_factory().create_routes())
app = Starlette(routes=routes)

CELERY_BROKER = os.environ.get("CELERY_BROKER")
if CELERY_BROKER is None:
    # Single node / developer mode
    LOGGER.info("No CELERY_BROKER set - running background tasks locally.")
    from servey.integration.local_schedule_app import mount_all

    mount_all()

