"""
Standard test mechanism for actions
"""
import inspect
from unittest import TestCase

from marshy import dump

from servey.action.action import Action
from servey.action.example import Example
from servey.action.util import get_marshaller_for_params
from servey.finder.action_finder_abc import find_actions


def _define_action_example_test(action_: Action, example: Example):
    def test(self):
        marshaller = get_marshaller_for_params(action_.fn, set())
        kwargs = marshaller.load(example.params)
        result = action_.fn(**kwargs)
        sig = inspect.signature(action_.fn)
        externalized_result = dump(result, sig.return_annotation)
        self.assertEqual(example.result, externalized_result)

    return test


def define_test_class():
    test_methods = {}
    for action in find_actions():
        for example in action.examples or []:
            if example.include_in_tests:
                test_methods[
                    "test_" + action.name + "__" + example.name
                ] = _define_action_example_test(action, example)
    test_class = type("TestServeyActions", (TestCase,), test_methods)
    return test_class
