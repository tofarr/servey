from dataclasses import dataclass
from typing import Callable, Optional


def noop(self):
    return [self]


@dataclass
class BatchInvoker:
    fn: Callable
    max_batch_size: int = 100
    arg_extractor: Optional[Callable] = noop
