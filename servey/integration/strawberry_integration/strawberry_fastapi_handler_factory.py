import logging
import os
from typing import Optional, Callable

from fastapi import FastAPI

from servey.action import Action
from servey.integration.fastapi_integration.executor_factory.fastapi_handler_factory_abc import (
    FastapiHandlerFactoryABC,
)
from servey.trigger.web_trigger import WebTrigger

LOGGER = logging.getLogger(__name__)


class StrawberryFastapiHandlerFactory(FastapiHandlerFactoryABC):
    graphql_path: str = os.environ.get("SERVEY_GRAPHQL_PATH") or "/graphql"
    debug: bool = int(os.environ.get("SERVER_DEBUG", "1")) == 1

    def create_handler_for_action(
        self, action: Action, trigger: WebTrigger
    ) -> Optional[Callable]:
        pass

    def mount_dependencies(self, api: FastAPI):
        try:
            from servey.integration.strawberry_integration.schema_factory import (
                new_schema_for_context,
            )
            from strawberry.asgi import GraphQL

            schema = new_schema_for_context()
            graphql_app = GraphQL(schema, debug=self.debug)
            api.add_route(self.graphql_path, graphql_app)
            api.add_websocket_route(self.graphql_path, graphql_app)
        except ModuleNotFoundError:
            LOGGER.info("Graphql not found - skipping")
