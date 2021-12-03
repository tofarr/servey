from abc import abstractmethod, ABC

from servey.request import Request
from servey.response import Response


class HandlerABC(ABC):
    priority: int = 100

    @abstractmethod
    def match(self, request: Request) -> bool:
        """ does this handler match the request given? """

    @abstractmethod
    def handle_request(self, request: Request) -> Response:
        """ handle the request given """

    @staticmethod
    def is_param_true(request: Request, param_name: str) -> bool:
        return request.get_param(param_name) in ['1', 'true']

    def __ne__(self, other):
        return self.priority != getattr(other, 'priority', None)

    def __lt__(self, other):
        return self.priority < getattr(other, 'priority', None)
