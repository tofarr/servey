import dataclasses
import inspect
from typing import Optional

from marshy.factory.optional_marshaller_factory import get_optional_type
from marshy.types import ExternalItemType

from servey.action.action import Action
from servey.errors import ServeyError
from servey.servey_aws.event_handler.event_handler_abc import (
    get_event_handlers,
    EventHandlerABC,
)
from servey.servey_aws.router.router_abc import RouterABC
from servey.util import to_snake_case


class AppsyncRouter(RouterABC):
    priority: int = 110

    def create_handler(self, event: ExternalItemType, context) -> EventHandlerABC:
        info = event.get("info", None)  # Diff appsync events
        if info is None:
            return
        field_name = info["fieldName"]
        source = event.get('source')
        if source:
            action = self.find_action_for_parent_type(info['parentTypeName'], field_name)
        else:
            action = self.find_action_for_field_name(field_name)
        if action is None:
            raise ServeyError(f"unknown_field_name:{field_name}")
        handlers = get_event_handlers(action)
        for handler in handlers:
            if handler.is_usable(event, context):
                return handler

    def find_action_for_parent_type(self, parent_type_name: str, field_name: str):
        field_name = to_snake_case(field_name)
        for action, trigger in self.web_trigger_actions:
            sig = inspect.signature(action.fn)
            parent_type = sig.return_annotation
            parent_type = get_optional_type(parent_type) or parent_type
            if getattr(parent_type, '__name__', None) == parent_type_name:
                fn = getattr(parent_type, field_name)
                sig = inspect.signature(fn)
                parameters = list(sig.parameters.values())
                parameters[0] = parameters[0].replace(annotation=parent_type)
                sig = sig.replace(parameters=parameters)

                def wrapper(*args, **kwargs):
                    return fn(*args, **kwargs)

                wrapper.__signature__ = sig
                action = dataclasses.replace(action, fn=wrapper)
                wrapper.__servey_action__ = action
                return action

    def find_action_for_field_name(self, field_name: str) -> Optional[Action]:
        for action, trigger in self.web_trigger_actions:
            action_field_name = action.name[0] + action.name.title()[1:].replace(
                "_", ""
            )
            if action_field_name == field_name:
                return action
