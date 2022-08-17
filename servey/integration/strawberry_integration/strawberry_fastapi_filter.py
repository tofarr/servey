import logging
import os
from inspect import Signature
from typing import Tuple

from fastapi import FastAPI

from servey.action import Action
from servey.integration.fastapi_integration.handler_filter.fastapi_handler_filter_abc import (
    FastapiHandlerFilterABC,
    ExecutorFn,
)
from servey.trigger.web_trigger import WebTrigger

LOGGER = logging.getLogger(__name__)


class StrawberryFastapiFilter(FastapiHandlerFilterABC):
    graphql_path: str = os.environ.get("SERVEY_GRAPHQL_PATH") or "/graphql"
    debug: bool = int(os.environ.get("SERVER_DEBUG", "1")) == 1

    def filter(
        self, action: Action, trigger: WebTrigger, fn: ExecutorFn, sig: Signature
    ) -> Tuple[ExecutorFn, Signature, bool]:
        return fn, sig, True

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
