"""
Standard test mechanism for actions
"""
import inspect
from unittest import TestCase

from marshy import dump

from servey.action.action import get_marshaller_for_params
from servey.example.example import Example
from servey.finder.action_finder_abc import find_actions
from servey.finder.found_action import FoundAction


def _define_action_example_test(action_: FoundAction, example: Example):
    def test(self):
        marshaller = get_marshaller_for_params(action_.fn)
        kwargs = marshaller.load(example.inputs)
        result = action_.fn(**kwargs)
        sig = inspect.signature(action_.fn)
        externalized_result = dump(result, sig.return_annotation)
        self.assertEqual(example.result, externalized_result)

    return test


def define_test_class():
    test_methods = {}
    for action in find_actions():
        for example in action.action_meta.examples or []:
            if example.include_in_tests:
                test_methods[
                    "test_" + action.action_meta.name + "__" + example.name
                ] = _define_action_example_test(action, example)
    test_class = type("TestServeyActions", (TestCase,), test_methods)
    return test_class
