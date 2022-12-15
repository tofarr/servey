import importlib
import inspect
import pkgutil
import os
from dataclasses import dataclass, field
from typing import Iterator

from servey.action.action import Action
from servey.finder.action_finder_abc import ActionFinderABC


@dataclass
class ModuleActionFinder(ActionFinderABC):
    """
    Default implementation of action_ finder which searches for actions in a particular module
    """

    root_module_name: str = field(
        default_factory=lambda: os.environ.get("SERVEY_ACTION_PATH") or "actions"
    )

    def find_actions(self) -> Iterator[Action]:
        module = importlib.import_module(self.root_module_name)
        yield from _find_actions_in_module(module)


def _find_actions_in_module(module) -> Iterator[Action]:
    for name, value in module.__dict__.items():
        if hasattr(value, "__servey_action__"):
            yield value.__servey_action__
    if not hasattr(module, "__path__"):
        return  # Module was not a package...
    paths = []
    paths.extend(module.__path__)
    module_infos = list(pkgutil.walk_packages(paths))
    for module_info in module_infos:
        sub_module_name = module.__name__ + "." + module_info.name
        sub_module = importlib.import_module(sub_module_name)
        # noinspection PyTypeChecker
        yield from _find_actions_in_module(sub_module)
