import os
from dataclasses import dataclass, field
from logging import getLogger
from typing import Iterator

from starlette.routing import Route, WebSocketRoute, Mount
from starlette.staticfiles import StaticFiles

from servey.servey_starlette.route_factory.route_factory_abc import (
    RouteFactoryABC,
)

LOGGER = getLogger(__name__)


@dataclass
class StrawberryStarletteRouteFactory(RouteFactoryABC):
    """Route factory which adds graphql"""

    graphql_path: str = field(
        default_factory=lambda: os.environ.get("SERVEY_GRAPHQL_PATH") or "/graphql"
    )
    debug: bool = field(
        default_factory=lambda: int(os.environ.get("SERVER_DEBUG", "1")) == 1
    )

    def create_routes(self) -> Iterator[Route]:
        # Create an authenticator object based on username and password
        try:
            from servey.servey_strawberry.schema_factory import (
                create_schema,
            )
            from strawberry.asgi import GraphQL

            schema = create_schema()
            if not schema:
                return
            graphql_app = GraphQL(schema, debug=self.debug)
            yield Route(path=self.graphql_path, methods=["post"], endpoint=graphql_app)
            yield WebSocketRoute(path=self.graphql_path, endpoint=graphql_app)
            if self.debug:
                # add as template route
                yield Mount(
                    "/graphiql",
                    app=StaticFiles(
                        packages=["servey.servey_strawberry"],
                        html=True,
                    ),
                    name="graphiql",
                )

        except ModuleNotFoundError:
            LOGGER.error("Graphql not found - skipping")
