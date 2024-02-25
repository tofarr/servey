from abc import ABC
from dataclasses import dataclass

from marshy import ExternalType
from marshy.marshaller.marshaller_abc import MarshallerABC, T


class SingletonABC(ABC):
    """Abstract singleton implementation"""

    def __new__(cls):
        instance = getattr(cls, "__instance", None)
        if instance is None:
            instance = object.__new__(cls)
            setattr(cls, "__instance", instance)
        return instance

    def __repr__(self):
        return self.__class__.__name__

    # pylint: disable=W0613
    # noinspection PyUnusedLocal
    @classmethod
    def __marshaller_factory__(cls, marshaller_context):
        return SingletonMarshaller(cls)


@dataclass
class SingletonMarshaller(MarshallerABC[T]):
    marshalled_type: T

    def load(self, item: ExternalType) -> T:
        return self.marshalled_type()

    def dump(self, item: T) -> ExternalType:
        return self.marshalled_type.__name__
