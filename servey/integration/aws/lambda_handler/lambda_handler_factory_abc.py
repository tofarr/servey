from abc import ABC, abstractmethod

from servey.action import Action
from servey.integration.aws.lambda_handler.lambda_handler_abc import LambdaHandlerABC


class LambdaHandlerFactory(ABC):
    @abstractmethod
    def create_lambda_handler(self, action: Action) -> LambdaHandlerABC:
        """Create a lambda handler for the action given"""
