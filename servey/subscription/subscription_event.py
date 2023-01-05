from typing import List, Union

from marshy.types import ExternalItemType
from schemey import Schema

from servey.action.util import move_ref_items_to_components
from servey.security.access_control.allow_none import ALLOW_NONE
from servey.subscription.subscription import Subscription


def subscription_event_schema(
    subscriptions: List[Subscription], components: ExternalItemType
) -> Schema:
    schemas = [s.event_schema for s in subscriptions if s.access_control != ALLOW_NONE]
    any_of = []
    for subscription in subscriptions:
        schema = subscription.event_schema.schema
        schema = move_ref_items_to_components(schema, schema, components)
        any_of.append(
            {
                "properties": {"type": {"const": type.__name__}, "payload": schema},
                "additionalProperties": False,
                "required": ["type", "payload"],
            }
        )
    type_ = Union[tuple(s.python_type for s in schemas)]
    return Schema({"anyOf": any_of}, type_)
