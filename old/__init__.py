import importlib
import pkgutil

CONFIG_MODULE_PREFIX = 'servey_config_'


def new_default_handler():
    module_info = (m for m in pkgutil.iter_modules() if m.name.startswith(CONFIG_MODULE_PREFIX))
    modules = [importlib.import_module(m.name) for m in module_info]
    modules.sort(key=lambda m: m.priority)
    handler = None
    for module in modules:
        handler = module.configure_handler(handler)
    return handler
