from abc import abstractmethod, ABC

from marshy import ExternalType


class ConnectorABC(ABC):

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
