import json
from functools import wraps
from typing import Callable, Dict, Optional, Any, TypeVar

from marshy.marshaller.marshaller_abc import MarshallerABC
from urllib import request

from servey.handler.action_handler import build_return_marshaller, build_params_marshaller

C = TypeVar('C', bound=Callable)


def http_callable(url: str,
                  method: str = 'POST',
                  params_marshaller: Optional[MarshallerABC] = None,
                  return_marshaller: Optional[MarshallerABC] = None,
                  header_factory: Optional[Callable[[], Dict[str, str]]] = None):
    def wrapper(callable_: C) -> C:
        nonlocal params_marshaller, return_marshaller
        if params_marshaller is None:
            params_marshaller = build_params_marshaller(callable_)
        if return_marshaller is None:
            return_marshaller = build_return_marshaller(callable_)

        @wraps(callable_)
        def wrapped(**kwargs):
            data = _encode_params(kwargs, params_marshaller)
            req = request.Request(url, data=data, method=method)
            if header_factory:
                for key, value in header_factory().items():
                    req.add_header(key, value)
            with request.urlopen(req) as response:
                result = _decode_result(response)
                return result

        return wrapped

    return wrapper

def _encode_params(params: Dict[str, Any], params_marshaller: MarshallerABC):
    dumped = params_marshaller.dump(params)
    json_data = json.dumps(dumped)
    encoded_data = json_data.encode('utf-8')
    return encoded_data


def _decode_result(response, return_marshaller: MarshallerABC):
    json_data = json.loads(response.read().decode())
    loaded = return_marshaller.load(json_data)
    return loaded
