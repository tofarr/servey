import importlib
import json
import logging
import os
from typing import Dict

from marshy.types import ExternalItemType, ExternalType

from servey.servey_aws.event_parser.event_parser_abc import EventParserABC
from servey.servey_aws.event_parser.factory.event_parser_factory_abc import (
    create_parser_factories,
)
from servey.servey_aws.result_render.factory.result_render_factory_abc import (
    create_render_factories,
)
from servey.servey_aws.result_render.result_render_abc import ResultRenderABC


def invoke(event: ExternalItemType, context) -> ExternalType:
    _LOGGER.info(json.dumps(dict(lambda_event=event)))
    parser = get_event_parser(event, context)
    render = get_result_render(event, context, parser)
    kwargs = parser.parse(event, context)
    result = _ACTION_FUNCTION(**kwargs)
    response = render.render(result)
    return response


def get_event_parser(event: Dict, context) -> EventParserABC:
    for factory in _EVENT_PARSER_FACTORIES:
        parser = factory.create(_ACTION_FUNCTION, event, context)
        if parser:
            return parser


def get_result_render(event: Dict, context, parser: EventParserABC) -> ResultRenderABC:
    for factory in _RESULT_RENDER_FACTORIES:
        render = factory.create(_ACTION_FUNCTION, event, context, parser)
        if render:
            return render


_ACTION_MODULE = importlib.import_module(os.environ["SERVEY_ACTION_MODULE"])
_ACTION_FUNCTION = getattr(_ACTION_MODULE, os.environ["SERVEY_ACTION_FUNCTION"])
_EVENT_PARSER_FACTORIES = create_parser_factories()
_RESULT_RENDER_FACTORIES = create_render_factories()
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)
