from dataclasses import dataclass
from typing import List

from servey.action.action import action
from servey.action.batch_invoker import BatchInvoker
from servey.trigger.web_trigger import WEB_GET


def _factorial(value: int) -> int:
    result = 1
    index = value
    while index > 1:
        result *= index
        index -= 1
    return result


def _factorial_all(values: List[int]) -> List[int]:
    results = [_factorial(v) for v in values]
    return results


@dataclass
class IntegerStats:
    value: int

    @action
    def factorial(self) -> int:
        """
        This demonstrates a resolvable field, lazily resolved (Usually by graphql)
        """
        return _factorial(self.value)

    @action(triggers=(WEB_GET,), batch_invoker=BatchInvoker(fn=_factorial_all))
    async def factorial_coroutine(self) -> int:
        """
        This demonstrates a resolvable field, lazily resolved (Usually by graphql)
        """
        return _factorial(self.value)
