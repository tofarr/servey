import dataclasses
import inspect
from dataclasses import is_dataclass, fields, dataclass, MISSING
from datetime import datetime
from decimal import Decimal
from typing import Type, Optional, Dict, Any, Callable, Union

import strawberry
from dateutil.relativedelta import relativedelta
from strawberry.dataloader import DataLoader, AbstractCache

from servey.action.action import Action, get_action
from servey.action.batch_invoker import BatchInvoker
from servey.cache_control.cache_control_abc import CacheControlABC
from servey.servey_strawberry.entity_factory.entity_factory_abc import (
    EntityFactoryABC,
)
from servey.servey_strawberry.schema_factory import SchemaFactory
from servey.servey_strawberry.schema_factory_lazy_input import SchemaFactoryLazyInput
from servey.servey_strawberry.schema_factory_lazy_type import SchemaFactoryLazyType


class DataclassFactory(EntityFactoryABC):
    priority: int = 120

    def create_type(
        self, annotation: Type, schema_factory: SchemaFactory
    ) -> Optional[Type]:
        if not is_dataclass(annotation):
            return
        # noinspection PyTypeChecker
        schema_factory.types[annotation.__name__] = SchemaFactoryLazyType(
            type_name=annotation.__name__, module="", schema_factory=schema_factory
        )

        annotations = {}
        params = {"__annotations__": annotations}
        # noinspection PyDataclass
        for f in fields(annotation):
            annotations[f.name] = schema_factory.get_type(f.type)

        # Check for functions decorated with @action
        for key, value in annotation.__dict__.items():
            resolvable = get_action(value)
            if resolvable:
                build_resolvable_field(resolvable, schema_factory, key, params)

        wrap_type = type(annotation.__name__, tuple(), params)
        type_ = strawberry.type(wrap_type)
        schema_factory.types[annotation.__name__] = type_
        # noinspection PyDataclass
        for field in fields(type_):
            field.type = schema_factory.get_type(field.type)
        return type_

    def create_input(
        self, annotation: Type, schema_factory: SchemaFactory
    ) -> Optional[Type]:
        if not is_dataclass(annotation):
            return
        name = f"{annotation.__name__}Input"
        input_ = schema_factory.inputs.get(name)
        if input_:
            return input_
        # noinspection PyTypeChecker
        schema_factory.inputs[name] = SchemaFactoryLazyInput(
            type_name=name, module="", schema_factory=schema_factory
        )

        annotations = {}
        params = {"__annotations__": annotations}
        # noinspection PyDataclass
        for f in fields(annotation):
            type_ = f.type
            if f.default is not MISSING:
                type_ = Optional[type_]
                if f.default is None or isinstance(
                    f.default, (str, int, bool, float, Decimal)
                ):
                    params[f.name] = f.default
            elif f.default_factory is not MISSING:
                type_ = Optional[type_]
                params[f.name] = dataclasses.field(default_factory=f.default_factory)
            annotations[f.name] = schema_factory.get_input(type_)

        # noinspection PyTypeChecker
        wrap_type = dataclass(type(name, tuple(), params))
        input_ = strawberry.input(wrap_type)
        schema_factory.inputs[name] = input_
        # noinspection PyDataclass
        for field in fields(input_):
            field.type = schema_factory.get_input(field.type)
        return input_


def build_resolvable_field(
    action: Action,
    schema_factory: SchemaFactory,
    key: str,
    params: Dict[str, Any],
):
    for handler_filter in schema_factory.handler_filters:
        action, continue_filtering = handler_filter.filter(action, schema_factory)
        if not continue_filtering:
            break

    fn = action.fn
    if action.batch_invoker:
        fn = _wrap_fn_in_data_loader(
            action.fn, action.batch_invoker, action.cache_control
        )
    sig = inspect.signature(fn)
    return_type = schema_factory.get_type(sig.return_annotation)
    params["__annotations__"][key] = return_type
    params[key] = strawberry.field(resolver=fn)


def _wrap_fn_in_data_loader(
    fn: Callable, batch_invoker: BatchInvoker, cache_control: CacheControlABC
):
    ttl = cache_control.ttl if hasattr(cache_control, "ttl") else 10
    data_loader = DataLoader(
        load_fn=batch_invoker.fn,
        max_batch_size=batch_invoker.max_batch_size,
        cache_map=_UserCache(relativedelta(seconds=ttl)),
    )

    sig = inspect.signature(fn)

    async def wrapper(self) -> sig.return_annotation:
        args = batch_invoker.arg_extractor(self)
        result = await data_loader.load(*args)
        return result

    return wrapper


@dataclass
class _UserCacheEntry:
    value: Any
    expire_at: datetime


class _UserCache(AbstractCache):
    def __init__(self, expire_in: relativedelta):
        self.cache: Dict[Any, _UserCacheEntry] = {}
        self.expire_in = expire_in

    def get(self, key: Any) -> Union[Any, None]:
        entry = self.cache.get(key)
        if entry and entry.expire_at > datetime.now():
            return entry.value

    def set(self, key: Any, value: Any) -> None:
        self.cache[key] = _UserCacheEntry(
            value, datetime.now() + self.expire_in
        )  # store data in the cache

    def delete(self, key: Any) -> None:
        del self.cache[key]  # delete key from the cache

    def clear(self) -> None:
        self.cache.clear()  # clear the cache
