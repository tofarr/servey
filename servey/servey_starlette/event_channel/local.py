from dataclasses import dataclass, field
from typing import Set, Optional, List, Dict

from starlette.websockets import WebSocket

from servey.event_channel.websocket.websocket_event_channel import WebsocketEventChannel
from servey.finder.event_channel_finder_abc import find_event_channels_by_type
from servey.security.authorization import Authorization


@dataclass
class LocalConnection:
    """A local websocket connection to event channels"""

    connection_id: str
    websocket: WebSocket
    channel_names: Set[str] = field(default_factory=set)
    authorization: Optional[Authorization] = None


@dataclass
class LocalChannelConnections:
    """All local connections to a single event channel"""

    channel: WebsocketEventChannel
    connections: List[LocalConnection] = field(default_factory=list)


CONNECTIONS_BY_NAME: Optional[Dict[str, LocalChannelConnections]] = None
CONNECTIONS_BY_ID: Dict[str, LocalConnection] = {}


# pylint: disable=W0603
def get_connections_by_name() -> Dict[str, LocalChannelConnections]:
    global CONNECTIONS_BY_NAME
    if CONNECTIONS_BY_NAME is None:
        CONNECTIONS_BY_NAME = {
            channel.name: LocalChannelConnections(channel)
            for channel in find_event_channels_by_type(WebsocketEventChannel)
        }
    return CONNECTIONS_BY_NAME


def get_connections_by_id() -> Dict[str, LocalConnection]:
    return CONNECTIONS_BY_ID
