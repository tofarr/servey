import importlib
import inspect
import pkgutil
import os
from typing import Iterator

from servey.action.finder.action_finder_abc import ActionFinderABC
from servey.action.finder.found_action import FoundAction


class ModuleActionFinder(ActionFinderABC):
    """
    Default implementation of action finder which searches for actions in a particular module
    """

    root_module_name: str = os.environ.get("SERVEY_ACTION_PATH") or "servey_actions"

    def find_actions(self) -> Iterator[FoundAction]:
        paths = []
        paths.extend(importlib.import_module(self.root_module_name).__path__)
        for module_info in pkgutil.walk_packages(paths):
            module_spec = module_info.module_finder.find_spec(module_info.name)
            module = module_spec.loader.load_module(module_info.name)
            for name, value in module.__dict__.items():
                if hasattr(value, "__servey_action_meta__"):
                    yield FoundAction(value.__servey_action_meta__, value)
                elif inspect.isclass(value):
                    for f_name, f_value in value.__dict__.items():
                        if hasattr(f_value, "__servey_action_meta__"):
                            yield FoundAction(
                                f_value.__servey_action_meta__, f_value, value
                            )
