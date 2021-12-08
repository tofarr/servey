import json
from dataclasses import dataclass
from http import HTTPStatus
from typing import Dict, Callable, Optional
from urllib import request

from marshy.marshaller.marshaller_abc import MarshallerABC
from marshy.marshaller.obj_marshaller import ObjMarshaller
from schemey.object_schema import ObjectSchema
from schemey.schema_abc import SchemaABC


@dataclass(frozen=True)
class HttpJsonRemoteCall:
    url: str
    params_marshaller: ObjMarshaller
    return_marshaller: MarshallerABC
    params_schema: ObjectSchema[Dict]
    return_schema: SchemaABC
    method: str = 'POST'
    header_factory: Optional[Callable[[], Dict[str, str]]] = None

    def __call__(self, **kwargs):
        self.params_schema.validate(kwargs)
        req = request.Request(self.url,
                              data=self.encode_kwargs(**kwargs),
                              method=self.method,
                              headers=self.header_factory() if self.header_factory else {})
        with request.urlopen(req) as response:
            if response.code != HTTPStatus.OK:
                raise ValueError(f'remote_call_error:{response.code}')
            return_value = self.decode_response(response)
            self.return_schema.validate(return_value)
            return return_value

    def encode_kwargs(self, **kwargs):
        dumped = self.params_marshaller.dump(kwargs)
        json_data = json.dumps(dumped)
        encoded_data = json_data.encode('utf-8')
        return encoded_data

    def decode_response(self, response):
        json_data = json.loads(response.read().decode())
        loaded = self.return_marshaller.load(json_data)
        return loaded
