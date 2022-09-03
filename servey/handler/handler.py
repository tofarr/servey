from marshy import ExternalType
from marshy.types import ExternalItemType

from servey.action import Action
from servey.handler.handler_abc import HandlerABC


class Handler(HandlerABC):
    action: Action

    def invoke(self, event: ExternalItemType) -> ExternalType:
        executor = self.action.create_executor()
        executor.execute(foo)
