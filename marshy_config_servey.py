from marshy.factory.impl_marshaller_factory import register_impl
from marshy.marshaller_context import MarshallerContext

from servey.authorizer.authorizer_abc import AuthorizerABC
from servey.authorizer.no_authorizer import NoAuthorizer
from servey.cache.cache_control_abc import CacheControlABC
from servey.cache.no_cache_control import NoCacheControl
from servey.connector.connector_meta import ConnectorMeta
from servey.connector.event.subscribe import Subscribe
from servey.connector.event.unsubscribe import Unsubscribe
from servey.connector.event.websocket_event_abc import WebsocketEventABC

priority = 100


def configure(context: MarshallerContext):
    register_impl(AuthorizerABC, NoAuthorizer, context)
    register_impl(CacheControlABC, NoCacheControl, context)
    register_impl(WebsocketEventABC, Subscribe, context)
    register_impl(WebsocketEventABC, Unsubscribe, context)
