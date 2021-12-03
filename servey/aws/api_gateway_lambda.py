from typing import Callable

from marshy.types import ExternalItemType

from servey import new_default_handler
from servey.handler.action_handler import action_handler
from servey.handler.handler_abc import HandlerABC
from servey.request import Request
from servey.response import Response


def api_gateway_handler_lambda_adapter(handler: HandlerABC):
    """
    Returns a lambda for invoking the handler given from api gateway
    """
    def callable_lambda(event, context):
        request = event_to_request(event)
        response = handler.handle_request(request)
        result = response_to_result(response)
        return result
    return callable_lambda


def api_gateway_lambda(callable_: Callable):
    handler = action_handler(callable_)
    lambda_function = api_gateway_handler_lambda_adapter(handler)
    return lambda_function


def root_api_gateway_lambda():
    handler = new_default_handler()
    lambda_function = api_gateway_handler_lambda_adapter(handler)
    return lambda_function


def event_to_request(event: ExternalItemType) -> Request:
    request = Request(
        method=event['httpMethod'],
        path=event['path'],
        headers=event.get('headers') or {},
        params=event.get('multiValueQueryStringParameters') or {},
        input=event.get('body')
    )
    return request


def response_to_result(response: Response) -> ExternalItemType:
    result = {
        'statusCode': response.code,
        'headers': response.headers,
        'body': response.content
    }
    return result
