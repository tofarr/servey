from abc import ABC, abstractmethod

from flask import Flask


class FlaskHandlerABC(ABC):

    @abstractmethod
    def register(self, flask: Flask):
        """ Register this handler with the servey_flask instance given """
