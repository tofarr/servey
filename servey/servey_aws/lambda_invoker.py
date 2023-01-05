import dataclasses
import importlib
import inspect
import json
import logging
import os
from marshy.types import ExternalItemType, ExternalType

from servey.action.action import get_action
from servey.errors import ServeyError
from servey.servey_aws.event_handler.event_handler_abc import get_event_handlers


def invoke(event: ExternalItemType, context) -> ExternalType:
    _LOGGER.info(json.dumps(dict(lambda_event=event)))
    for handler in _EVENT_HANDLERS:
        if handler.is_usable(event, context):
            return handler.handle(event, context)
    raise ServeyError("no_handler")


def find_action():
    action_module = importlib.import_module(os.environ["SERVEY_ACTION_MODULE"])
    action_function_name = os.environ["SERVEY_ACTION_FUNCTION_NAME"]
    if "." in action_function_name:
        action_class_name, action_function_name = action_function_name.split(".")
        action_class = getattr(action_module, action_class_name)
        action_function = getattr(action_class, action_function_name)
        action_ = get_action(action_function)
        fn = action_.fn

        def wrapper(*args, **kwargs):
            result = fn(*args, **kwargs)
            return result

        sig = inspect.signature(fn)
        sig = sig.replace(
            parameters=[
                p.replace(annotation=action_class) if p.name == "self" else p
                for p in sig.parameters.values()
            ]
        )
        wrapper.__signature__ = sig
        action_ = dataclasses.replace(action_, fn=wrapper)
        return action_
    else:
        action_function = getattr(action_module, action_function_name)
        action_ = get_action(action_function)
        return action_


_ACTION = find_action()
_EVENT_HANDLERS = get_event_handlers(_ACTION)
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)
