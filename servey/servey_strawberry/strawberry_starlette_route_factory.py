import os
from dataclasses import dataclass
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

    graphql_path: str = os.environ.get("SERVEY_GRAPHQL_PATH") or "/graphql"
    debug: bool = int(os.environ.get("SERVER_DEBUG", "1")) == 1

    def create_routes(self) -> Iterator[Route]:
        # Create an authenticator object based on username and password
        try:
            from servey.servey_strawberry.schema_factory import (
                new_schema_for_actions,
            )
            from strawberry.asgi import GraphQL

            schema = new_schema_for_actions()
            graphql_app = GraphQL(schema, debug=self.debug)
            yield Route(path=self.graphql_path, methods=["post"], endpoint=graphql_app)
            yield WebSocketRoute(path=self.graphql_path, endpoint=graphql_app)
            if self.debug:
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
