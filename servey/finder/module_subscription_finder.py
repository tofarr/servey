import importlib
import logging
import pkgutil
from dataclasses import dataclass, field
from typing import Iterator

from servey.finder.subscription_finder_abc import SubscriptionFinderABC
from servey.subscription.subscription import Subscription
from servey.util import get_servey_main

LOGGER = logging.getLogger(__name__)


@dataclass
class ModuleSubscriptionFinder(SubscriptionFinderABC):
    """
    Default implementation of subscription finder which searches for channels in a particular module
    """

    root_module_name: str = field(
        default_factory=lambda: f"{get_servey_main()}.subscriptions"
    )

    def find_subscriptions(self) -> Iterator[Subscription]:
        try:
            module = importlib.import_module(self.root_module_name)
            # noinspection PyTypeChecker
            yield from _find_subscriptions_in_module(module)
        except ModuleNotFoundError as e:
            LOGGER.info(f"no_subscriptions_found:{e}")


def _find_subscriptions_in_module(module) -> Iterator[Subscription]:
    for name, value in module.__dict__.items():
        if isinstance(value, Subscription):
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
        yield from _find_subscriptions_in_module(sub_module)
