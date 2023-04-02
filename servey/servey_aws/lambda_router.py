"""
Invoker which groups lambdas together in such a way that one lambda may be used to invoke multiple
different actions. Routers are used to try and link an event to an action, which may be specific
to APIGateway, AppSync, or Direct Invocation
"""
import json
import logging
from marshy.types import ExternalItemType, ExternalType

from servey.errors import ServeyError
from servey.servey_aws.router.router_abc import find_routers


def invoke(event: ExternalItemType, context) -> ExternalType:
    _LOGGER.info(json.dumps(dict(lambda_event=event)))
    for router in _ROUTERS:
        handler = router.create_handler(event, context)
        if handler:
            return handler.handle(event, context)
    raise ServeyError("no_handler")


_ROUTERS = find_routers()
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)
