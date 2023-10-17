import importlib
import logging
import pkgutil
from dataclasses import dataclass, field
from typing import Iterator

from servey.event_channel.event_channel_abc import EventChannelABC
from servey.finder.event_channel_finder_abc import EventChannelFinderABC
from servey.util import get_servey_main

LOGGER = logging.getLogger(__name__)


@dataclass
class ModuleEventChannelFinder(EventChannelFinderABC):
    """
    Default implementation of channel finder which searches for channels in a particular module
    """

    root_module_name: str = field(
        default_factory=lambda: f"{get_servey_main()}.event_channels"
    )

    def find_event_channels(self) -> Iterator[EventChannelABC]:
        try:
            module = importlib.import_module(self.root_module_name)
            # noinspection PyTypeChecker
            yield from _find_event_channels_in_module(module)
        except ModuleNotFoundError as e:
            LOGGER.info(f"no_channels_found:{e}")


def _find_event_channels_in_module(module) -> Iterator[EventChannelABC]:
    for value in module.__dict__.values():
        if isinstance(value, EventChannelABC):
            yield value
    if not hasattr(module, "__path__"):
        return  # Module was not a package...
    paths = []
    paths.extend(module.__path__)
    module_infos = list(pkgutil.walk_packages(paths))
    for module_info in module_infos:
        sub_module_name = module.__name__ + "." + module_info.name
        sub_module = importlib.import_module(sub_module_name)
        # noinspection PyTypeChecker
        yield from _find_event_channels_in_module(sub_module)
