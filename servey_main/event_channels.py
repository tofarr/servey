from servey.action.action import get_action
from servey.event_channel.background.background_action_channel import (
    background_action_channel,
)

from servey.event_channel.websocket.websocket_event_channel import (
    websocket_event_channel,
)

# pylint: disable=cyclic-import

messenger = websocket_event_channel("messenger", str)

# Lazy initialization to avoid cyclic import
_printer = None

def get_printer():
    """Get the printer event channel, initializing it if needed."""
    global _printer  # pylint: disable=global-statement
    if _printer is None:
        from servey_main.actions import print_consumer  # pylint: disable=import-outside-toplevel
        _printer = background_action_channel(get_action(print_consumer))
    return _printer

# For backward compatibility
class PrinterProxy:
    """Proxy object that delegates to the lazily-initialized printer."""
    def publish(self, event):
        return get_printer().publish(event)

    def __getattr__(self, name):
        return getattr(get_printer(), name)

printer = PrinterProxy()
