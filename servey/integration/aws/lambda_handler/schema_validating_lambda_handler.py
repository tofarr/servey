from dataclasses import dataclass

from marshy import ExternalType
from marshy.types import ExternalItemType

from servey.action import Action
from servey.integration.aws.lambda_handler.lambda_handler_abc import LambdaHandlerABC


@dataclass
class SchemaValidatingLambdaHandler(LambdaHandlerABC):
    lambda_handler: LambdaHandlerABC

    def __call__(self, event: ExternalItemType, context) -> ExternalType:
        action_meta = self.lambda_handler.get_action().action_meta
        action_meta.params_schema.validate(event)
        result = self.lambda_handler.__call__(event, context)
        action_meta.result_schema.validate(result)
        return result

    def get_action(self) -> Action:
        return self.lambda_handler.get_action()
