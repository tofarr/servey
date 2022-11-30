from abc import ABC, abstractmethod
from typing import Dict, Any

from marshy.types import ExternalItemType


class EventParserABC(ABC):
    @abstractmethod
    def parse(self, event: ExternalItemType, context) -> Dict[str, Any]:
        """Parse kwargs from an event"""
