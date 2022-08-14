import importlib
import pkgutil
import os
from typing import Iterator

from servey.action import Action
from servey.action_finder.action_finder_abc import ActionFinderABC


class ModuleActionFinder(ActionFinderABC):
    """
    Default implementation of action finder which searches for actions in a particular module
    """

    root_module_name: str = os.environ.get("SERVEY_ACTION_PATH") or "servey_actions"

    def find_actions(self) -> Iterator[Action]:
        paths = []
        paths.extend(importlib.import_module(self.root_module_name).__path__)
        for module_info in pkgutil.walk_packages(paths):
            module_spec = module_info.module_finder.find_spec(module_info.name)
            module = module_spec.loader.load_module(module_info.name)
            for name, value in module.__dict__.items():
                if hasattr(value, "__servey_action_meta__"):
                    yield Action(value)
