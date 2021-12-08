from dataclasses import dataclass
from typing import Dict, List, Optional

from marshy import ExternalType


@dataclass
class Request:
    method: str
    path: List[str]
    headers: Dict[str, str]
    params: Dict[str, List[str]]
    input: Optional[str] = None

    def get_param(self, name: str) -> Optional[str]:
        values = self.params.get(name)
        if values:
            return values[0]
