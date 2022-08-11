"""
Utility for locating actions anywhere in the path. These actions may then be mounted using aws lambda and API gateway
(via serverless), using foobar (via FastAPI), or through some other means.
"""
import importlib
import pkgutil
from dataclasses import dataclass
import os
from types import ModuleType
from typing import List, Iterator

from servey.action import Action
from servey.servey_error import ServeyError


@dataclass
class FoundAction:
    module: ModuleType
    action_name: str
    action: Action


def find_actions(modules: List[str]) -> Iterator[FoundAction]:
    paths = []
    for m in modules:
        paths.extend(importlib.import_module(m).__path__)
    for module_info in pkgutil.walk_packages(paths):
        module_spec = module_info.module_finder.find_spec(module_info.name)
        module = module_spec.loader.load_module(module_info.name)
        for name, value in module.__dict__.items():
            if isinstance(value, Action):
                yield FoundAction(module, name, value)


def find_default_actions() -> Iterator[FoundAction]:
    servey_action_path = os.environ.get('SERVEY_ACTION_PATH')
    if servey_action_path is None:
        raise ServeyError('Please specify SERVEY_ACTION_PATH in your environment. (Tell us where to look for actions!)')
    return find_actions([servey_action_path])
