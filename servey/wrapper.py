import importlib
import inspect
import logging
import pkgutil
from typing import Optional, Callable, Iterator, Tuple

from marshy import get_default_context
from marshy.marshaller_context import MarshallerContext
from schemey.schema_context import SchemaContext, get_default_schema_context

from servey.action import action, Action
from servey.authorizer.authorizer_abc import AuthorizerABC
from servey.authorizer.no_authorizer import NoAuthorizer
from servey.cache.cache_control_abc import CacheControlABC
from servey.cache.no_cache_control import NoCacheControl
from servey.graphql_type import GraphqlType
from servey.http_method import HttpMethod
from servey.publisher import Publisher

logger = logging.getLogger(__name__)


def wrap_action(callable_: Callable = None,
                name: Optional[str] = None,
                marshaller_context: Optional[MarshallerContext] = None,
                schema_context: Optional[SchemaContext] = None,
                path: Optional[str] = None,
                http_methods: Tuple[HttpMethod, ...] = (HttpMethod.GET,),
                graphql_type: Optional[GraphqlType] = None,
                cache_control: CacheControlABC = NoCacheControl(),
                authorizer: AuthorizerABC = NoAuthorizer()  # Not sure if this should be the default
                ) -> Callable:
    """ Wrap a callable (Typically a module function) so that it can be found by find_actions """
    def wrapper(to_wrap: Callable):
        action_ = action(to_wrap, name, marshaller_context, schema_context, path, http_methods, graphql_type,
                         cache_control, authorizer)
        to_wrap.__action__ = action_
        return to_wrap

    return wrapper if callable_ is None else wrapper(callable_)


def find_actions(path: str = '') -> Iterator[Action]:
    """
    Recursively, find all actions from module functions in the module designated. This will load all submodules,
    so will be a slow operation.
    """
    return _find_all_in_module(path, '__action__')


def wrap_publisher(callable_: Callable = None,
                   marshaller_context: Optional[MarshallerContext] = None,
                   schema_context: Optional[SchemaContext] = None):
    if marshaller_context is None:
        marshaller_context = get_default_context()
    if schema_context is None:
        schema_context = get_default_schema_context()

    def wrapper(to_wrap: Callable = None):
        sig = inspect.signature(to_wrap)
        keys = list(sig.parameters.keys())
        if len(keys) != 1:
            raise ValueError('publisher_must_have_single_arg')
        event_key = next(keys)
        event_type = sig.parameters[event_key].annotation
        publisher = Publisher(
            name=to_wrap.__name__,
            doc=to_wrap.__doc__,
            event_marshaller=marshaller_context.get_marshaller(event_type),
            event_schema=schema_context.get_schema(event_type)
        )
        publish = publisher.publish
        publish.__publisher__ = publisher
        return publish

    return wrapper if callable_ is None else wrapper(callable_)


def find_publishers(path: str = '') -> Iterator[Publisher]:
    """
    Recursively, find all actions from module functions in the module designated. This will load all submodules,
    so will be a slow operation.
    """
    return _find_all_in_module(path, '__publisher__')


def _find_all_in_module(module_name: str, attr_name: str):
    try:
        module = importlib.import_module(module_name.replace('/', '.'))
        for key, value in module.__dict__.items():
            if key.startswith('_'):  # Skip private / dunder attributes
                continue
            if not isinstance(value, Callable):
                continue
            result = getattr(value, attr_name, None)
            if result:
                yield result
        for module_info in pkgutil.iter_modules([module_name.replace('.', '/')]):
            logger.info(f'Searching for config in module:{module_name}')
            yield from _find_all_in_module(f"{module_name}.{module_info.name}", attr_name)
    except ModuleNotFoundError:
        return
