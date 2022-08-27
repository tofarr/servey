import dataclasses
from typing import Type, Optional

from marshy.factory.optional_marshaller_factory import get_optional_type

from servey.access_control.authorization import Authorization
from servey.action import Action


def get_authorization_field_name(action: Action) -> Optional[str]:
    if action.method_name and dataclasses.is_dataclass(action.subject):
        for f in dataclasses.fields(action.subject):
            annotation = f.type
            annotation = get_optional_type(annotation)
            if annotation == Authorization:
                return f.name


def get_authorization_kwarg_name(action: Action) -> Optional[str]:
    params = action.get_signature().parameters.values()
    for param in params:
        if is_authorization(param.annotation):
            return param.name


def is_authorization(annotation: Type) -> bool:
    annotation = get_optional_type(annotation) or annotation
    return annotation == Authorization
