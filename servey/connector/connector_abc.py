from abc import abstractmethod, ABC
from typing import Iterator, Optional

from marshy import ExternalType

from servey.connector.connection_info import ConnectionInfo


class ConnectorABC(ABC):
    """
     Connector for events to / from external destinations. Typically implemented by some sort of websocket. Example
     implementations include AWS API Gateway and low level websocket.

     Note that no methods are provided at this level for determining who is connected, or whether they have received
     messages or not - the intention is that is provided by higher level layers.
     """

    @abstractmethod
    def send(self, channel_key: str, event: ExternalType):
        """ Publish an event to the channel given. """

    @abstractmethod
    def get_connection_info(self, connection_id: str) -> Optional[ConnectionInfo]:
        """ Get the connection info under the id given """

    @abstractmethod
    def get_all_connection_info(self, connection_id: str) -> Iterator[ConnectionInfo]:
        """ Get info on all connections """

    @abstractmethod
    def subscribe(self, connection_id: str, channel_key: str):
        """ Subscribe a connection to a channel """

    @abstractmethod
    def unsubscribe(self, connection_id: str, channel_key: str):
        """ Unsubscribe a connection from a channel """
