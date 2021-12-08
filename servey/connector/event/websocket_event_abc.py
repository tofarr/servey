from abc import ABC, abstractmethod

from servey.connector.connector_abc import ConnectorABC


class WebsocketEventABC(ABC):
    """ Marker class for websocket events """

    @abstractmethod
    def process(self, connector: ConnectorABC, connection_id: str):
        """ Process a event received over a websocket """
