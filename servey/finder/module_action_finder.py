import importlib
import logging
import pkgutil
from dataclasses import dataclass, is_dataclass, field
from typing import Iterator

from servey.action.action import Action, get_action
from servey.finder.action_finder_abc import ActionFinderABC
from servey.util import get_servey_main

LOGGER = logging.getLogger(__name__)


@dataclass
class ModuleActionFinder(ActionFinderABC):
    """
    Default implementation of action_ finder which searches for actions in a particular module
    """

    root_module_name: str = field(
        default_factory=lambda: f"{get_servey_main()}.actions"
    )

    def find_actions(self) -> Iterator[Action]:
        try:
            module = importlib.import_module(self.root_module_name)
            # noinspection PyTypeChecker
            yield from _find_actions_in_module(module)
        except ModuleNotFoundError as e:
            LOGGER.warning(f"no_actions_found:{e}")


def _find_actions_in_module(module) -> Iterator[Action]:
    for name, value in module.__dict__.items():
        action = get_action(value)
        if action:
            yield action
        if type(value) == type and is_dataclass(value):
            for param_name, param_value in value.__dict__.items():
                action = get_action(param_value)
                if action:
                    yield action
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
