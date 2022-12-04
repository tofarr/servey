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
        module = __import__(self.root_module_name)
        yield from _find_actions_in_module(module)


def _find_actions_in_module(module) -> Iterator[FoundAction]:
    for name, value in module.__dict__.items():
        if hasattr(value, "__servey_action_meta__"):
            yield FoundAction(value.__servey_action_meta__, value)
        elif inspect.isclass(value):
            for f_name, f_value in value.__dict__.items():
                if hasattr(f_value, "__servey_action_meta__"):
                    yield FoundAction(f_value.__servey_action_meta__, f_value, value)
    if not hasattr(module, "__path__"):
        return  # Module was not a package...
    paths = []
    paths.extend(module.__path__)
    module_infos = list(pkgutil.walk_packages(paths))
    for module_info in module_infos:
        sub_module_name = module.__name__ + "." + module_info.name
        sub_module = importlib.import_module(sub_module_name)
        yield from _find_actions_in_module(sub_module)
