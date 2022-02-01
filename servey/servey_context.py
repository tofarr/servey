import importlib
import pkgutil
from dataclasses import field, dataclass
from typing import Dict, Optional

from servey.action import Action
from servey.connector.connector_abc import ConnectorABC
from servey.publisher import Publisher


@dataclass
class ServeyContext:
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    actions_by_name: Dict[str, Action] = field(default_factory=dict)
    publishers_by_name: Dict[str, Publisher] = field(default_factory=dict)
    connector: ConnectorABC = None


FACTORY_ENV_VAR = 'SERVEY_CONTEXT_FACTORY'

CONFIG_MODULE_PREFIX = 'servey_config_'
_default_context = None


def get_default_servey_context() -> ServeyContext:
    global _default_context
    if not _default_context:
        _default_context = new_default_servey_context()
    return _default_context


def new_default_servey_context() -> ServeyContext:
    context = ServeyContext()
    # Set up context based on naming convention
    module_info = (m for m in pkgutil.iter_modules() if m.name.startswith(CONFIG_MODULE_PREFIX))
    modules = [importlib.import_module(m.name) for m in module_info]
    modules.sort(key=lambda m: m.priority, reverse=True)
    for m in modules:
        getattr(m, 'configure_servey')(context)
    if context.publishers_by_name and not context.connector:
        raise ValueError('publishers_require_connector')
    return context
