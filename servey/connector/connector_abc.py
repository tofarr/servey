from abc import abstractmethod, ABC
from typing import Optional, Iterator

from marshy import ExternalType

from servey.connector.connection_info import ConnectionInfo
from servey.connector.connector_meta import ConnectorMeta


class ConnectorABC(ABC):

    @abstractmethod
    def get_meta(self) -> ConnectorMeta:
        """ Get meta for this connector """

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
