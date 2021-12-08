from marshy.marshaller.deferred_marshaller import DeferredMarshaller
from marshy.marshaller.union_marshaller import UnionMarshaller
from marshy.marshaller_context import MarshallerContext

from servey.connector.event.subscribe import Subscribe
from servey.connector.event.unsubscribe import Unsubscribe
from servey.connector.event.websocket_event_abc import WebsocketEventABC

priority = 100


def configure(context: MarshallerContext):
    context.register_marshaller(UnionMarshaller(
        WebsocketEventABC,
        {
            Subscribe.__name__: DeferredMarshaller(Subscribe, context),
            Unsubscribe.__name__: DeferredMarshaller(Unsubscribe, context)
        }
    ))
