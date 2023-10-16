from servey.event_channel.background.background_action_channel import (
    background_action_channel,
)
from servey.event_channel.websocket.websocket_channel import websocket_channel
from servey.security.access_control.scope_access_control import ScopeAccessControl
from tests.specs.number_spec.actions import integer_stats_consumer
from tests.specs.number_spec.models import IntegerStats


integer_stats_for_admins = websocket_channel(
    event_type=IntegerStats,
    name="integer_stats_for_admins",
    access_control=ScopeAccessControl("root"),
)


integer_stats_queue = background_action_channel(
    action=integer_stats_consumer,
    name="integer_stats_queue",
)
